# LegalGuard Backend API Contracts

Base URL: `http://127.0.0.1:5000`

Protected endpoints require an authenticated Flask session.

## Health

| Method | Endpoint | Auth | Success |
|---|---|---|---|
| GET | `/api/health` | No | `200` |
| GET | `/api/health/db` | No | `200` |

`GET /api/health`:
```json
{"service":"legalguard-backend","status":"ok"}