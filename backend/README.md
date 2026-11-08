# PaisaDiary Backend

FastAPI backend scaffold for PaisaDiary.

## Requirements
- Python 3.11+
- PostgreSQL 16+ (or Docker Compose)

## Local setup (PowerShell)
```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
Copy-Item ..\.env.example ..\.env
uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs

## Tests
```powershell
python -m pytest
```

This scaffold intentionally does not yet implement financial CRUD or authentication. Those are next increments and must be backed by migrations and tests.
