# MetaMark Deployment Guide (Software-Only)

This guide provides step-by-step instructions to deploy MetaMark to production using cloud platforms.

## 1. Database Setup (PlanetScale / Hosted MySQL)
1. Provision a MySQL database instance via PlanetScale, Aiven, or Railway.
2. Execute `backend/database/schema.sql` to initialize tables (`users`, `products`, `images`, `selleractivity`, `gifts`, `gifts_redeemed`).
3. Obtain the connection URI and credentials.

## 2. Backend Deployment (Render / Railway)
1. Link your GitHub repository to Render or Railway.
2. Set build directory to root and runtime to **Python 3.11**.
3. Set start command: `gunicorn backend.api.app:app`.
4. Configure Environment Variables:
   - `DB_HOST`: Hosted MySQL hostname
   - `DB_USER`: Database username
   - `DB_PASSWORD`: Database password
   - `DB_NAME`: Database name
   - `FLASK_SECRET_KEY`: Production secret key
   - `GOOGLE_API_KEY`: API key for Gemini 2.0 & Vision API
   - `CORS_ALLOWED_ORIGINS`: Production frontend Vercel URL (and extension origins)

## 3. Frontend Deployment (Vercel)
1. Import the repository into Vercel and select `frontend/` as the root folder.
2. Framework Preset: **Next.js**.
3. Configure Environment Variables:
   - `NEXT_PUBLIC_API_BASE_URL`: Your deployed backend production URL (e.g., `https://metamark-backend.onrender.com`).
4. Trigger deployment.

## 4. Extension Production Setup
1. In `extension/popup.js` settings, update `API_BASE_URL` to point to the production backend URL.
2. Load unpacked extension via `chrome://extensions` for manual client distribution.