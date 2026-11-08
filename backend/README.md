# PaisaDiary Backend

FastAPI backend foundation for PaisaDiary.

## Requirements
- Python 3.11+
- Docker Desktop (for PostgreSQL 16)
- Git

## Start PostgreSQL (PowerShell)
From repository root:
```powershell
docker compose up -d postgres
```

## Local backend setup
```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
Copy-Item ..\.env.example ..\.env
```

Set the `JWT_SECRET_KEY` in `../.env` to a strong random secret before exposing the service.

## Database migrations
```powershell
alembic upgrade head
```

## Run API
```powershell
uvicorn app.main:app --reload
```

Open API docs: http://localhost:8000/docs

## Tests
```powershell
python -m pytest
```

## Implemented routes
- `GET /api/v1/health`
- `GET /api/v1/ready`
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- Authenticated account CRUD/read balance routes
- Authenticated income/expense transaction create/list routes

## Security notes
- Passwords are hashed with Argon2 via pwdlib.
- Access JWT expires in 15 minutes.
- User-specific finance APIs require a Bearer token.
- The default JWT secret is for local development only and is rejected when `ENVIRONMENT=production`.
- Email verification, rate limiting, refresh/revocation, and production deployment hardening remain outstanding.

This is a foundation, not a production-ready financial service yet.
