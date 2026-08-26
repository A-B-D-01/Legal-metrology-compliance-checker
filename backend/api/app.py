import json
import os

import mysql.connector
from dotenv import load_dotenv
from flask import Flask, jsonify, request, session
from flask_cors import CORS
from mysql.connector import Error
from werkzeug.security import check_password_hash, generate_password_hash

from backend.scraper.scraper import (
    ScraperBlockedError,
    ScraperError,
    ScraperStructureError,
    ScraperTimeoutError,
    scrape_page,
)


load_dotenv()


def get_db_connection():
    """Create and return a MySQL connection."""
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME", "legalguard"),
        )

        if connection.is_connected():
            return connection

    except Error as error:
        print(f"Database connection error: {error}")

    return None


def require_auth():
    """Return an authentication error if the user is not logged in."""
    if not session.get("logged_in"):
        return jsonify({
            "error": "Authentication required",
            "message": "Please log in first.",
        }), 401

    return None


def serialize_json_field(value):
    """Convert a MySQL JSON field into a Python object."""
    if value is None:
        return None

    if isinstance(value, (dict, list)):
        return value

    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value

    return value


def serialize_product(product):
    """Make product JSON fields safe for API responses."""
    if "violations" in product:
        product["violations"] = serialize_json_field(
            product["violations"]
        )

    return product


def serialize_activity(activity):
    """Make activity JSON fields safe for API responses."""
    if "details" in activity:
        activity["details"] = serialize_json_field(
            activity["details"]
        )

    return activity


def create_app():
    app = Flask(__name__)

    # ==============================================================
    # CONFIGURATION
    # ==============================================================

    app.config["SECRET_KEY"] = os.getenv(
        "FLASK_SECRET_KEY",
        "development-only-change-me",
    )

    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    CORS(app)

    # ==============================================================
    # HEALTH
    # ==============================================================

    @app.get("/api/health")
    def health():
        return jsonify({
            "status": "ok",
            "service": "legalguard-backend",
        }), 200

    @app.get("/api/health/db")
    def database_health():
        connection = get_db_connection()

        if connection is None:
            return jsonify({
                "status": "error",
                "database": "disconnected",
            }), 503

        cursor = None

        try:
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()

            return jsonify({
                "status": "ok",
                "database": "connected",
            }), 200

        except Error:
            return jsonify({
                "status": "error",
                "database": "query_failed",
            }), 503

        finally:
            if cursor:
                cursor.close()
            connection.close()

    # ==============================================================
    # AUTHENTICATION - SIGNUP
    # ==============================================================

    @app.post("/api/signup")
    def signup():
        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({
                "error": "Invalid request",
                "message": "Request body must be a JSON object.",
            }), 400

        name = data.get("name")
        email = data.get("email")
        password = data.get("password")

        if not isinstance(name, str) or not name.strip():
            return jsonify({
                "error": "Invalid name",
                "message": "Name is required.",
            }), 400

        if not isinstance(email, str) or not email.strip():
            return jsonify({
                "error": "Invalid email",
                "message": "Email is required.",
            }), 400

        if not isinstance(password, str) or not password:
            return jsonify({
                "error": "Invalid password",
                "message": "Password is required.",
            }), 400

        if len(password) < 8:
            return jsonify({
                "error": "Invalid password",
                "message": "Password must be at least 8 characters.",
            }), 400

        name = name.strip()
        email = email.strip().lower()

        connection = get_db_connection()

        if connection is None:
            return jsonify({
                "error": "Database unavailable",
                "message": "Unable to connect to the database.",
            }), 503

        cursor = None

        try:
            cursor = connection.cursor(dictionary=True)

            cursor.execute(
                "SELECT id FROM users WHERE email = %s",
                (email,),
            )

            if cursor.fetchone():
                return jsonify({
                    "error": "Email already registered",
                    "message": "An account with this email already exists.",
                }), 409

            password_hash = generate_password_hash(password)

            cursor.execute(
                """
                INSERT INTO users (
                    name,
                    email,
                    password_hash
                )
                VALUES (%s, %s, %s)
                """,
                (name, email, password_hash),
            )

            connection.commit()

            return jsonify({
                "success": True,
                "message": "Account created successfully.",
            }), 201

        except Error:
            connection.rollback()

            return jsonify({
                "error": "Database error",
                "message": "Unable to create the account.",
            }), 500

        finally:
            if cursor:
                cursor.close()

            connection.close()

    # ==============================================================
    # AUTHENTICATION - LOGIN
    # ==============================================================

    @app.post("/api/login")
    def login():
        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({
                "error": "Invalid request",
                "message": "Request body must be a JSON object.",
            }), 400

        email = data.get("email")
        password = data.get("password")

        if not isinstance(email, str) or not email.strip():
            return jsonify({
                "error": "Invalid email",
                "message": "Email is required.",
            }), 400

        if not isinstance(password, str) or not password:
            return jsonify({
                "error": "Invalid password",
                "message": "Password is required.",
            }), 400

        email = email.strip().lower()

        connection = get_db_connection()

        if connection is None:
            return jsonify({
                "error": "Database unavailable",
                "message": "Unable to connect to the database.",
            }), 503

        cursor = None

        try:
            cursor = connection.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT
                    id,
                    name,
                    email,
                    password_hash,
                    role,
                    mt_tokens
                FROM users
                WHERE email = %s
                """,
                (email,),
            )

            user = cursor.fetchone()

            if not user:
                return jsonify({
                    "error": "Invalid credentials",
                    "message": "Email or password is incorrect.",
                }), 401

            if not check_password_hash(
                user["password_hash"],
                password,
            ):
                return jsonify({
                    "error": "Invalid credentials",
                    "message": "Email or password is incorrect.",
                }), 401

            session["logged_in"] = True
            session["user_id"] = user["id"]
            session["user_email"] = user["email"]
            session["role"] = user["role"]

            return jsonify({
                "success": True,
                "message": "Login successful.",
                "user": {
                    "id": user["id"],
                    "name": user["name"],
                    "email": user["email"],
                    "role": user["role"],
                    "mt_tokens": user["mt_tokens"],
                },
            }), 200

        except Error:
            return jsonify({
                "error": "Database error",
                "message": "Unable to process login.",
            }), 500

        finally:
            if cursor:
                cursor.close()

            connection.close()

    # ==============================================================
    # AUTHENTICATION - LOGOUT
    # ==============================================================

    @app.post("/api/logout")
    def logout():
        session.clear()

        return jsonify({
            "success": True,
            "message": "Logout successful.",
        }), 200

    # ==============================================================
    # AUTHENTICATION - CURRENT USER
    # ==============================================================

    @app.get("/api/me")
    def current_user():
        auth_error = require_auth()

        if auth_error:
            return auth_error

        connection = get_db_connection()

        if connection is None:
            return jsonify({
                "error": "Database unavailable",
                "message": "Unable to connect to the database.",
            }), 503

        cursor = None

        try:
            cursor = connection.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT
                    id,
                    name,
                    email,
                    role,
                    mt_tokens,
                    created_at
                FROM users
                WHERE id = %s
                """,
                (session["user_id"],),
            )

            user = cursor.fetchone()

            if not user:
                session.clear()

                return jsonify({
                    "error": "User not found",
                    "message": "The authenticated user no longer exists.",
                }), 404

            return jsonify({
                "success": True,
                "user": user,
            }), 200

        except Error:
            return jsonify({
                "error": "Database error",
                "message": "Unable to fetch user information.",
            }), 500

        finally:
            if cursor:
                cursor.close()

            connection.close()

    # ==============================================================
    # PRODUCTS
    # ==============================================================

    @app.get("/api/products")
    def get_products():
        auth_error = require_auth()

        if auth_error:
            return auth_error

        connection = get_db_connection()

        if connection is None:
            return jsonify({
                "error": "Database unavailable",
                "message": "Unable to connect to the database.",
            }), 503

        cursor = None

        try:
            cursor = connection.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT
                    id,
                    seller_id,
                    name,
                    brand,
                    price,
                    mrp,
                    net_quantity,
                    compliance_score,
                    compliance_status,
                    source_url,
                    created_at,
                    updated_at
                FROM products
                ORDER BY created_at DESC
                """
            )

            products = cursor.fetchall()

            return jsonify({
                "success": True,
                "products": [
                    serialize_product(product)
                    for product in products
                ],
                "count": len(products),
            }), 200

        except Error:
            return jsonify({
                "error": "Database error",
                "message": "Unable to fetch products.",
            }), 500

        finally:
            if cursor:
                cursor.close()

            connection.close()

    @app.get("/api/products/detailed")
    def get_detailed_products():
        auth_error = require_auth()

        if auth_error:
            return auth_error

        connection = get_db_connection()

        if connection is None:
            return jsonify({
                "error": "Database unavailable",
                "message": "Unable to connect to the database.",
            }), 503

        cursor = None

        try:
            cursor = connection.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT
                    p.id,
                    p.seller_id,
                    p.name,
                    p.brand,
                    p.description,
                    p.price,
                    p.mrp,
                    p.net_quantity,
                    p.manufacturer,
                    p.country_of_origin,
                    p.compliance_score,
                    p.compliance_status,
                    p.violations,
                    p.source_url,
                    p.created_at,
                    p.updated_at,
                    u.name AS seller_name,
                    u.email AS seller_email
                FROM products p
                INNER JOIN users u
                    ON p.seller_id = u.id
                ORDER BY p.created_at DESC
                """
            )

            products = cursor.fetchall()

            return jsonify({
                "success": True,
                "products": [
                    serialize_product(product)
                    for product in products
                ],
                "count": len(products),
            }), 200

        except Error:
            return jsonify({
                "error": "Database error",
                "message": "Unable to fetch detailed products.",
            }), 500

        finally:
            if cursor:
                cursor.close()

            connection.close()

    @app.get("/api/product/<int:product_id>")
    def get_product(product_id):
        auth_error = require_auth()

        if auth_error:
            return auth_error

        connection = get_db_connection()

        if connection is None:
            return jsonify({
                "error": "Database unavailable",
                "message": "Unable to connect to the database.",
            }), 503

        cursor = None

        try:
            cursor = connection.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT
                    p.id,
                    p.seller_id,
                    p.name,
                    p.brand,
                    p.description,
                    p.price,
                    p.mrp,
                    p.net_quantity,
                    p.manufacturer,
                    p.country_of_origin,
                    p.compliance_score,
                    p.compliance_status,
                    p.violations,
                    p.source_url,
                    p.created_at,
                    p.updated_at,
                    u.name AS seller_name,
                    u.email AS seller_email
                FROM products p
                INNER JOIN users u
                    ON p.seller_id = u.id
                WHERE p.id = %s
                """,
                (product_id,),
            )

            product = cursor.fetchone()

            if not product:
                return jsonify({
                    "error": "Product not found",
                    "message": "No product exists with the given ID.",
                }), 404

            return jsonify({
                "success": True,
                "product": serialize_product(product),
            }), 200

        except Error:
            return jsonify({
                "error": "Database error",
                "message": "Unable to fetch the product.",
            }), 500

        finally:
            if cursor:
                cursor.close()

            connection.close()

    @app.get("/api/image/<int:image_id>")
    def get_image(image_id):
        auth_error = require_auth()

        if auth_error:
            return auth_error

        connection = get_db_connection()

        if connection is None:
            return jsonify({
                "error": "Database unavailable",
                "message": "Unable to connect to the database.",
            }), 503

        cursor = None

        try:
            cursor = connection.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT
                    id,
                    product_id,
                    image_url,
                    created_at
                FROM images
                WHERE id = %s
                """,
                (image_id,),
            )

            image = cursor.fetchone()

            if not image:
                return jsonify({
                    "error": "Image not found",
                    "message": "No image exists with the given ID.",
                }), 404

            return jsonify({
                "success": True,
                "image": image,
            }), 200

        except Error:
            return jsonify({
                "error": "Database error",
                "message": "Unable to fetch the image.",
            }), 500

        finally:
            if cursor:
                cursor.close()

            connection.close()

    # ==============================================================
    # SELLER ACTIVITY
    # ==============================================================

    @app.get("/api/seller/activity")
    def seller_activity():
        auth_error = require_auth()

        if auth_error:
            return auth_error

        connection = get_db_connection()

        if connection is None:
            return jsonify({
                "error": "Database unavailable",
                "message": "Unable to connect to the database.",
            }), 503

        cursor = None

        try:
            cursor = connection.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT
                    sa.id,
                    sa.seller_id,
                    sa.product_id,
                    sa.activity_type,
                    sa.details,
                    sa.created_at,
                    p.name AS product_name
                FROM selleractivity sa
                LEFT JOIN products p
                    ON sa.product_id = p.id
                WHERE sa.seller_id = %s
                ORDER BY sa.created_at DESC
                """,
                (session["user_id"],),
            )

            activities = cursor.fetchall()

            return jsonify({
                "success": True,
                "activities": [
                    serialize_activity(activity)
                    for activity in activities
                ],
                "count": len(activities),
            }), 200

        except Error:
            return jsonify({
                "error": "Database error",
                "message": "Unable to fetch seller activity.",
            }), 500

        finally:
            if cursor:
                cursor.close()

            connection.close()

    # ==============================================================
    # HEATMAP
    # ==============================================================

    @app.get("/api/heatmap")
    def heatmap():
        auth_error = require_auth()

        if auth_error:
            return auth_error

        connection = get_db_connection()

        if connection is None:
            return jsonify({
                "error": "Database unavailable",
                "message": "Unable to connect to the database.",
            }), 503

        cursor = None

        try:
            cursor = connection.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT
                    compliance_status,
                    COUNT(*) AS product_count,
                    AVG(compliance_score) AS average_score
                FROM products
                WHERE seller_id = %s
                GROUP BY compliance_status
                ORDER BY compliance_status
                """,
                (session["user_id"],),
            )

            rows = cursor.fetchall()

            data = [
                {
                    "compliance_status": row["compliance_status"],
                    "product_count": row["product_count"],
                    "average_score": (
                        float(row["average_score"])
                        if row["average_score"] is not None
                        else None
                    ),
                }
                for row in rows
            ]

            return jsonify({
                "success": True,
                "data": data,
            }), 200

        except Error:
            return jsonify({
                "error": "Database error",
                "message": "Unable to generate heatmap data.",
            }), 500

        finally:
            if cursor:
                cursor.close()

            connection.close()

    # ==============================================================
    # GLOBAL HEATMAP
    # ==============================================================

    @app.get("/api/global-heatmap")
    def global_heatmap():
        auth_error = require_auth()

        if auth_error:
            return auth_error

        connection = get_db_connection()

        if connection is None:
            return jsonify({
                "error": "Database unavailable",
                "message": "Unable to connect to the database.",
            }), 503

        cursor = None

        try:
            cursor = connection.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT
                    compliance_status,
                    COUNT(*) AS product_count,
                    AVG(compliance_score) AS average_score
                FROM products
                GROUP BY compliance_status
                ORDER BY compliance_status
                """
            )

            rows = cursor.fetchall()

            data = [
                {
                    "compliance_status": row["compliance_status"],
                    "product_count": row["product_count"],
                    "average_score": (
                        float(row["average_score"])
                        if row["average_score"] is not None
                        else None
                    ),
                }
                for row in rows
            ]

            return jsonify({
                "success": True,
                "data": data,
            }), 200

        except Error:
            return jsonify({
                "error": "Database error",
                "message": "Unable to generate global heatmap data.",
            }), 500

        finally:
            if cursor:
                cursor.close()

            connection.close()

    # ==============================================================
    # SCRAPER
    # ==============================================================

    @app.post("/api/scrape")
    def scrape():
        auth_error = require_auth()

        if auth_error:
            return auth_error

        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({
                "error": "Invalid request",
                "message": "Request body must be a JSON object.",
            }), 400

        url = data.get("url")

        if not isinstance(url, str) or not url.strip():
            return jsonify({
                "error": "Invalid URL",
                "message": "A URL is required.",
            }), 400

        timeout = data.get("timeout", 15)

        if isinstance(timeout, bool) or not isinstance(timeout, int):
            return jsonify({
                "error": "Invalid timeout",
                "message": "Timeout must be an integer.",
            }), 400

        if timeout <= 0 or timeout > 60:
            return jsonify({
                "error": "Invalid timeout",
                "message": "Timeout must be between 1 and 60 seconds.",
            }), 400

        try:
            result = scrape_page(
                url.strip(),
                timeout=timeout,
            )

            return jsonify({
                "success": True,
                "data": result,
            }), 200

        except ValueError as error:
            return jsonify({
                "error": "Invalid URL",
                "message": str(error),
            }), 400

        except ScraperTimeoutError:
            return jsonify({
                "error": "Scraper timeout",
                "message": "The webpage took too long to load.",
            }), 504

        except ScraperBlockedError:
            return jsonify({
                "error": "Scraper blocked",
                "message": (
                    "The target website appears to have "
                    "blocked the scraper."
                ),
            }), 403

        except ScraperStructureError:
            return jsonify({
                "error": "Page structure changed",
                "message": (
                    "The webpage did not contain usable content."
                ),
            }), 422

        except ScraperError:
            return jsonify({
                "error": "Scraper error",
                "message": "Unable to retrieve the webpage.",
            }), 502

        # ==============================================================
    # GIFTS - LIST
    # ==============================================================

    @app.get("/api/gifts")
    def get_gifts():
        auth_error = require_auth()

        if auth_error:
            return auth_error

        connection = get_db_connection()

        if connection is None:
            return jsonify({
                "error": "Database unavailable",
                "message": "Unable to connect to the database.",
            }), 503

        cursor = None

        try:
            cursor = connection.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT
                    id,
                    name,
                    description,
                    token_cost,
                    stock,
                    image_url,
                    created_at
                FROM gifts
                ORDER BY created_at DESC
                """
            )

            gifts = cursor.fetchall()

            return jsonify({
                "success": True,
                "gifts": gifts,
                "count": len(gifts),
            }), 200

        except Error:
            return jsonify({
                "error": "Database error",
                "message": "Unable to fetch gifts.",
            }), 500

        finally:
            if cursor:
                cursor.close()

            connection.close()

    # ==============================================================
    # GIFTS - CREATE
    # ==============================================================

    @app.post("/api/gifts")
    def create_gift():
        auth_error = require_auth()

        if auth_error:
            return auth_error

        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({
                "error": "Invalid request",
                "message": "Request body must be a JSON object.",
            }), 400

        name = data.get("name")
        description = data.get("description")
        token_cost = data.get("token_cost")
        stock = data.get("stock", 0)
        image_url = data.get("image_url")

        if not isinstance(name, str) or not name.strip():
            return jsonify({
                "error": "Invalid name",
                "message": "Gift name is required.",
            }), 400

        if isinstance(token_cost, bool) or not isinstance(token_cost, int):
            return jsonify({
                "error": "Invalid token_cost",
                "message": "token_cost must be an integer.",
            }), 400

        if token_cost <= 0:
            return jsonify({
                "error": "Invalid token_cost",
                "message": "token_cost must be greater than zero.",
            }), 400

        if isinstance(stock, bool) or not isinstance(stock, int):
            return jsonify({
                "error": "Invalid stock",
                "message": "stock must be an integer.",
            }), 400

        if stock < 0:
            return jsonify({
                "error": "Invalid stock",
                "message": "stock cannot be negative.",
            }), 400

        if description is not None and not isinstance(description, str):
            return jsonify({
                "error": "Invalid description",
                "message": "description must be a string.",
            }), 400

        if image_url is not None and not isinstance(image_url, str):
            return jsonify({
                "error": "Invalid image_url",
                "message": "image_url must be a string.",
            }), 400

        connection = get_db_connection()

        if connection is None:
            return jsonify({
                "error": "Database unavailable",
                "message": "Unable to connect to the database.",
            }), 503

        cursor = None

        try:
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO gifts (
                    name,
                    description,
                    token_cost,
                    stock,
                    image_url
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    name.strip(),
                    description.strip() if isinstance(description, str) else None,
                    token_cost,
                    stock,
                    image_url.strip() if isinstance(image_url, str) else None,
                ),
            )

            connection.commit()

            gift_id = cursor.lastrowid

            return jsonify({
                "success": True,
                "message": "Gift created successfully.",
                "gift_id": gift_id,
            }), 201

        except Error:
            connection.rollback()

            return jsonify({
                "error": "Database error",
                "message": "Unable to create gift.",
            }), 500

        finally:
            if cursor:
                cursor.close()

            connection.close()

    # ==============================================================
    # GIFTS - TOKEN BALANCE
    # ==============================================================

    @app.get("/api/gifts/token-balance")
    def token_balance():
        auth_error = require_auth()

        if auth_error:
            return auth_error

        connection = get_db_connection()

        if connection is None:
            return jsonify({
                "error": "Database unavailable",
                "message": "Unable to connect to the database.",
            }), 503

        cursor = None

        try:
            cursor = connection.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT mt_tokens
                FROM users
                WHERE id = %s
                """,
                (session["user_id"],),
            )

            user = cursor.fetchone()

            if not user:
                return jsonify({
                    "error": "User not found",
                    "message": "The authenticated user does not exist.",
                }), 404

            return jsonify({
                "success": True,
                "mt_tokens": user["mt_tokens"],
            }), 200

        except Error:
            return jsonify({
                "error": "Database error",
                "message": "Unable to fetch token balance.",
            }), 500

        finally:
            if cursor:
                cursor.close()

            connection.close()

    # ==============================================================
    # GIFTS - ADD TOKENS
    # ==============================================================

    @app.post("/api/gifts/add-tokens")
    def add_tokens():
        auth_error = require_auth()

        if auth_error:
            return auth_error

        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({
                "error": "Invalid request",
                "message": "Request body must be a JSON object.",
            }), 400

        tokens = data.get("tokens")

        if isinstance(tokens, bool) or not isinstance(tokens, int):
            return jsonify({
                "error": "Invalid tokens",
                "message": "tokens must be an integer.",
            }), 400

        if tokens <= 0:
            return jsonify({
                "error": "Invalid tokens",
                "message": "tokens must be greater than zero.",
            }), 400

        connection = get_db_connection()

        if connection is None:
            return jsonify({
                "error": "Database unavailable",
                "message": "Unable to connect to the database.",
            }), 503

        cursor = None

        try:
            cursor = connection.cursor(dictionary=True)

            cursor.execute(
                """
                UPDATE users
                SET mt_tokens = mt_tokens + %s
                WHERE id = %s
                """,
                (tokens, session["user_id"]),
            )

            connection.commit()

            cursor.execute(
                """
                SELECT mt_tokens
                FROM users
                WHERE id = %s
                """,
                (session["user_id"],),
            )

            user = cursor.fetchone()

            return jsonify({
                "success": True,
                "message": "Tokens added successfully.",
                "added_tokens": tokens,
                "mt_tokens": user["mt_tokens"],
            }), 200

        except Error:
            connection.rollback()

            return jsonify({
                "error": "Database error",
                "message": "Unable to add tokens.",
            }), 500

        finally:
            if cursor:
                cursor.close()

            connection.close()

    # ==============================================================
    # GIFTS - REDEEM
    # ==============================================================

    @app.post("/api/gifts/<int:gift_id>/redeem")
    def redeem_gift(gift_id):
        auth_error = require_auth()

        if auth_error:
            return auth_error

        connection = get_db_connection()

        if connection is None:
            return jsonify({
                "error": "Database unavailable",
                "message": "Unable to connect to the database.",
            }), 503

        cursor = None

        try:
            cursor = connection.cursor(dictionary=True)

            # Lock the gift row and user row during redemption.
            cursor.execute(
                """
                SELECT
                    id,
                    name,
                    token_cost,
                    stock
                FROM gifts
                WHERE id = %s
                FOR UPDATE
                """,
                (gift_id,),
            )

            gift = cursor.fetchone()

            if not gift:
                connection.rollback()

                return jsonify({
                    "error": "Gift not found",
                    "message": "No gift exists with the given ID.",
                }), 404

            if gift["stock"] <= 0:
                connection.rollback()

                return jsonify({
                    "error": "Out of stock",
                    "message": "This gift is currently out of stock.",
                }), 409

            cursor.execute(
                """
                SELECT
                    id,
                    mt_tokens
                FROM users
                WHERE id = %s
                FOR UPDATE
                """,
                (session["user_id"],),
            )

            user = cursor.fetchone()

            if not user:
                connection.rollback()

                return jsonify({
                    "error": "User not found",
                    "message": "The authenticated user does not exist.",
                }), 404

            if user["mt_tokens"] < gift["token_cost"]:
                connection.rollback()

                return jsonify({
                    "error": "Insufficient tokens",
                    "message": "You do not have enough tokens to redeem this gift.",
                    "required_tokens": gift["token_cost"],
                    "available_tokens": user["mt_tokens"],
                }), 409

            cursor.execute(
                """
                UPDATE users
                SET mt_tokens = mt_tokens - %s
                WHERE id = %s
                """,
                (gift["token_cost"], user["id"]),
            )

            cursor.execute(
                """
                UPDATE gifts
                SET stock = stock - 1
                WHERE id = %s
                """,
                (gift_id,),
            )

            cursor.execute(
                """
                INSERT INTO gifts_redeemed (
                    user_id,
                    gift_id,
                    tokens_spent,
                    status
                )
                VALUES (%s, %s, %s, 'redeemed')
                """,
                (
                    user["id"],
                    gift_id,
                    gift["token_cost"],
                ),
            )

            redemption_id = cursor.lastrowid

            connection.commit()

            return jsonify({
                "success": True,
                "message": "Gift redeemed successfully.",
                "redemption": {
                    "id": redemption_id,
                    "gift_id": gift_id,
                    "gift_name": gift["name"],
                    "tokens_spent": gift["token_cost"],
                    "status": "redeemed",
                },
            }), 200

        except Error:
            connection.rollback()

            return jsonify({
                "error": "Database error",
                "message": "Unable to redeem gift.",
            }), 500

        finally:
            if cursor:
                cursor.close()

            connection.close()

    # ==============================================================
    # GIFTS - MY REDEMPTIONS
    # ==============================================================

    @app.get("/api/gifts/my-redemptions")
    def my_redemptions():
        auth_error = require_auth()

        if auth_error:
            return auth_error

        connection = get_db_connection()

        if connection is None:
            return jsonify({
                "error": "Database unavailable",
                "message": "Unable to connect to the database.",
            }), 503

        cursor = None

        try:
            cursor = connection.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT
                    gr.id,
                    gr.user_id,
                    gr.gift_id,
                    g.name AS gift_name,
                    g.description AS gift_description,
                    gr.tokens_spent,
                    gr.status,
                    gr.redeemed_at
                FROM gifts_redeemed gr
                INNER JOIN gifts g
                    ON gr.gift_id = g.id
                WHERE gr.user_id = %s
                ORDER BY gr.redeemed_at DESC
                """,
                (session["user_id"],),
            )

            redemptions = cursor.fetchall()

            return jsonify({
                "success": True,
                "redemptions": redemptions,
                "count": len(redemptions),
            }), 200

        except Error:
            return jsonify({
                "error": "Database error",
                "message": "Unable to fetch redemption history.",
            }), 500

        finally:
            if cursor:
                cursor.close()

            connection.close()

    # ==============================================================
    # ERROR HANDLERS
    # ==============================================================

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "error": "Bad request",
            "message": str(error.description),
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "error": "Not found",
            "message": "The requested endpoint does not exist.",
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "error": "Method not allowed",
            "message": (
                "This HTTP method is not supported "
                "for this endpoint."
            ),
        }), 405

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            "error": "Internal server error",
            "message": "An unexpected error occurred.",
        }), 500

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
    )