# PaisaDiary Implementation Status

**Canonical specification:** [PRODUCT_BLUEPRINT.md](./PRODUCT_BLUEPRINT.md)  
**Active branch:** `feat/phase-1-foundation`  
**Current phase:** Phase 1 — Financial Foundation

## Progress

### Increment 0 — Product specification
- [x] Canonical product blueprint committed
- [x] Feature branch established
- [x] Existing repository inspected

### Increment 1 — Backend scaffold
- [x] FastAPI application, settings, health endpoints
- [x] PostgreSQL Docker Compose and .env template
- [x] pytest tests and CI workflow
- [ ] CI run observed green

### Increment 2 — Persistence and initial finance domain
- [x] SQLAlchemy base and session factory
- [x] User, account, category, transaction models
- [x] Integer paise amount storage and positive amount constraint
- [x] Income/expense semantics and balance service
- [x] Initial Alembic configuration and schema migration
- [x] Database-backed readiness probe
- [ ] Migration run against actual PostgreSQL
- [ ] DB integration test run verified

### Increment 3 — Authentication foundation
- [x] Registration endpoint
- [x] Login endpoint
- [x] Argon2 password hashing via pwdlib
- [x] Short-lived JWT access token (15 minutes)
- [x] Current-user token validation dependency
- [x] Auth API tests added
- [ ] CI/test execution verified
- [ ] Refresh token/session revocation (later security increment)

## Current API
- `GET /`
- `GET /api/v1/health`
- `GET /api/v1/ready` — checks PostgreSQL with `SELECT 1`
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`

## Important limitations / next steps
- Account and transaction CRUD APIs are not yet exposed.
- JWT secret has a development-only default. Set a strong `JWT_SECRET_KEY` in `.env` before deployment; do not use the default in production.
- No local test runner or PostgreSQL instance has been executed from this environment. CI is configured, but results must be checked before calling the implementation verified.
- Registration currently has no email verification or rate limiting. Add abuse protection before public production deployment.

## Financial architecture decisions
- Store monetary amounts as integer paise, never binary floats.
- Transaction amount is a positive magnitude; transaction type determines direction.
- Transfers, loans, repayments, and refunds need explicit semantics before implementing those endpoints.
- AI must not calculate authoritative balances or change financial records without user intent.
- Every finance endpoint must scope records to the authenticated user.
