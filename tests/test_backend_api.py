import pytest

from backend.api.app import create_app


class FakeCursor:
    def __init__(self, rows=None):
        self.rows = rows or []
        self.executed = []
        self.lastrowid = 1

    def execute(self, query, params=None):
        self.executed.append((query, params))

    def fetchone(self):
        if self.rows:
            return self.rows[0]
        return None

    def fetchall(self):
        return self.rows

    def close(self):
        pass


class FakeConnection:
    def __init__(self, rows=None):
        self.cursor_obj = FakeCursor(rows)
        self.committed = False
        self.rolled_back = False

    def cursor(self, dictionary=False):
        return self.cursor_obj

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

    def close(self):
        pass


@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key",
    })
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def login_session(client):
    with client.session_transaction() as session:
        session["logged_in"] = True
        session["user_id"] = 1
        session["user_email"] = "test@example.com"
        session["role"] = "seller"


# ==============================================================
# HEALTH
# ==============================================================


def test_health(client):
    response = client.get("/api/health")

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "ok"
    assert data["service"] == "legalguard-backend"


# ==============================================================
# AUTH
# ==============================================================


def test_signup(client, monkeypatch):
    fake_connection = FakeConnection([])

    monkeypatch.setattr(
        "backend.api.app.get_db_connection",
        lambda: fake_connection,
    )

    response = client.post(
        "/api/signup",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "TestPassword123",
        },
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["success"] is True
    assert data["message"] == "Account created successfully."

    assert fake_connection.committed is True


def test_signup_validation(client):
    response = client.post(
        "/api/signup",
        json={
            "email": "test@example.com",
            "password": "TestPassword123",
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Invalid name"


def test_login(client, monkeypatch):
    from werkzeug.security import generate_password_hash

    fake_user = {
        "id": 1,
        "name": "Test User",
        "email": "test@example.com",
        "password_hash": generate_password_hash(
            "TestPassword123"
        ),
        "role": "seller",
        "mt_tokens": 100,
    }

    fake_connection = FakeConnection([fake_user])

    monkeypatch.setattr(
        "backend.api.app.get_db_connection",
        lambda: fake_connection,
    )

    response = client.post(
        "/api/login",
        json={
            "email": "test@example.com",
            "password": "TestPassword123",
        },
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert data["user"]["email"] == "test@example.com"

    with client.session_transaction() as session:
        assert session["logged_in"] is True
        assert session["user_id"] == 1


def test_login_invalid_password(client, monkeypatch):
    from werkzeug.security import generate_password_hash

    fake_user = {
        "id": 1,
        "name": "Test User",
        "email": "test@example.com",
        "password_hash": generate_password_hash(
            "CorrectPassword123"
        ),
        "role": "seller",
        "mt_tokens": 100,
    }

    fake_connection = FakeConnection([fake_user])

    monkeypatch.setattr(
        "backend.api.app.get_db_connection",
        lambda: fake_connection,
    )

    response = client.post(
        "/api/login",
        json={
            "email": "test@example.com",
            "password": "WrongPassword123",
        },
    )

    assert response.status_code == 401


def test_logout(client):
    login_session(client)

    response = client.post("/api/logout")

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True

    with client.session_transaction() as session:
        assert "logged_in" not in session


# ==============================================================
# SCRAPE
# ==============================================================


def test_scrape_requires_auth(client):
    response = client.post(
        "/api/scrape",
        json={
            "url": "https://example.com",
        },
    )

    assert response.status_code == 401


def test_scrape_success(client, monkeypatch):
    login_session(client)

    fake_result = {
        "url": "https://example.com",
        "title": "Example Domain",
        "page_length": 544,
        "load_time_seconds": 0.1,
    }

    monkeypatch.setattr(
        "backend.api.app.scrape_page",
        lambda url, timeout=15: fake_result,
    )

    response = client.post(
        "/api/scrape",
        json={
            "url": "https://example.com",
        },
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert data["data"]["title"] == "Example Domain"


def test_scrape_invalid_url(client):
    login_session(client)

    response = client.post(
        "/api/scrape",
        json={
            "url": "",
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Invalid URL"


# ==============================================================
# PRODUCTS
# ==============================================================


def test_products_requires_auth(client):
    response = client.get("/api/products")

    assert response.status_code == 401


def test_products(client, monkeypatch):
    login_session(client)

    fake_products = [
        {
            "id": 1,
            "seller_id": 1,
            "name": "Bath Soap",
            "brand": "TestBrand",
            "price": "45.00",
            "mrp": "50.00",
            "net_quantity": "100 g",
            "compliance_score": "85.50",
            "compliance_status": "compliant",
            "source_url": "https://example.com/product",
            "created_at": None,
            "updated_at": None,
        }
    ]

    fake_connection = FakeConnection(fake_products)

    monkeypatch.setattr(
        "backend.api.app.get_db_connection",
        lambda: fake_connection,
    )

    response = client.get("/api/products")

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert data["count"] == 1
    assert len(data["products"]) == 1
    assert data["products"][0]["name"] == "Bath Soap"


def test_detailed_products(client, monkeypatch):
    login_session(client)

    fake_products = [
        {
            "id": 1,
            "seller_id": 1,
            "name": "Bath Soap",
            "brand": "TestBrand",
            "description": "Test product",
            "price": "45.00",
            "mrp": "50.00",
            "net_quantity": "100 g",
            "manufacturer": "Test Manufacturer",
            "country_of_origin": "India",
            "compliance_score": "85.50",
            "compliance_status": "compliant",
            "violations": [],
            "source_url": "https://example.com/product",
            "created_at": None,
            "updated_at": None,
            "seller_name": "Test User",
            "seller_email": "test@example.com",
        }
    ]

    fake_connection = FakeConnection(fake_products)

    monkeypatch.setattr(
        "backend.api.app.get_db_connection",
        lambda: fake_connection,
    )

    response = client.get("/api/products/detailed")

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert data["count"] == 1
    assert data["products"][0]["seller_name"] == "Test User"


def test_product_by_id(client, monkeypatch):
    login_session(client)

    fake_product = {
        "id": 1,
        "seller_id": 1,
        "name": "Bath Soap",
        "brand": "TestBrand",
        "description": "Test product",
        "price": "45.00",
        "mrp": "50.00",
        "net_quantity": "100 g",
        "manufacturer": "Test Manufacturer",
        "country_of_origin": "India",
        "compliance_score": "85.50",
        "compliance_status": "compliant",
        "violations": [],
        "source_url": "https://example.com/product",
        "created_at": None,
        "updated_at": None,
        "seller_name": "Test User",
        "seller_email": "test@example.com",
    }

    fake_connection = FakeConnection([fake_product])

    monkeypatch.setattr(
        "backend.api.app.get_db_connection",
        lambda: fake_connection,
    )

    response = client.get("/api/product/1")

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert data["product"]["id"] == 1
    assert data["product"]["name"] == "Bath Soap"


def test_product_not_found(client, monkeypatch):
    login_session(client)

    fake_connection = FakeConnection([])

    monkeypatch.setattr(
        "backend.api.app.get_db_connection",
        lambda: fake_connection,
    )

    response = client.get("/api/product/999")

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Product not found"