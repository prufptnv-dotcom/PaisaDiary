# PaisaDiary Implementation Status

**Canonical spec:** [PRODUCT_BLUEPRINT.md](./PRODUCT_BLUEPRINT.md)  
**Branch:** `feat/phase-1-foundation`  
**Phase:** Phase 1 — Financial Foundation

## Completed increments

### Backend scaffold
- [x] FastAPI app, settings, health endpoints
- [x] PostgreSQL Docker Compose and .env template
- [x] CI workflow (PostgreSQL service + migrations + pytest)

### Persistence and finance domain
- [x] SQLAlchemy base/session
- [x] User, account, category, transaction ORM models
- [x] Integer paise backed by BigInteger
- [x] Initial Alembic schema migration
- [x] Deterministic user-scoped account balance calculation
- [x] Database readiness check

### Authentication
- [x] Registration and login endpoints
- [x] Argon2 password hashing
- [x] JWT access tokens (15-minute expiry)
- [x] Current-user dependency
- [x] Reject default JWT secret in production config

### Authenticated finance APIs
- [x] Account create/list/get/update
- [x] Account balance endpoint
- [x] Transaction create/list with filters
- [x] Ownership validation for account/category/transaction access
- [x] Currency must match selected account
- [x] Transaction category type must match income/expense

## API endpoints currently implemented
- `GET /`
- `GET /api/v1/health`
- `GET /api/v1/ready`
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/accounts`
- `GET /api/v1/accounts`
- `GET /api/v1/accounts/{account_id}`
- `PATCH /api/v1/accounts/{account_id}`
- `GET /api/v1/accounts/{account_id}/balance`
- `POST /api/v1/transactions`
- `GET /api/v1/transactions`

## Verification status
- [x] Unit/API test files added
- [x] CI workflow configured to run PostgreSQL migration and pytest
- [ ] GitHub Actions run confirmed green
- [ ] Local/PostgreSQL tests manually verified

**Important:** Code has been committed to GitHub, but tests have not yet been executed in this assistant environment. Do not label the branch production-ready.

## Remaining Phase 1 work
- [ ] Verify CI results and fix any failures
- [ ] Category list/create endpoints and default categories
- [ ] Transaction detail/update/reversal workflow
- [ ] Summary endpoint (income, expense, net cash flow)
- [ ] Authorization regression tests for cross-user access
- [ ] API docs and error response consistency
- [ ] Security hardening (rate limiting, token/session revocation, email verification)
- [ ] Review and create PR; keep main unchanged until review

## Financial rules
- Money: integer paise / PostgreSQL BigInteger, never floats.
- Transaction amount is positive magnitude; type determines add/subtract.
- Transfers, refunds, loans and repayments require explicit models/semantics.
- AI never owns authoritative arithmetic.
- Every finance query must be scoped to authenticated user.
