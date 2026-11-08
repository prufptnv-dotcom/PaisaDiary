# PaisaDiary Implementation Status

**Canonical spec:** [PRODUCT_BLUEPRINT.md](./PRODUCT_BLUEPRINT.md)  
**Branch:** `feat/phase-1-foundation`  
**Phase:** Phase 1 — Financial Foundation

## Implemented
- [x] FastAPI scaffold, config, health/readiness probes
- [x] PostgreSQL Docker Compose and Alembic initial migration
- [x] SQLAlchemy models: user, account, category, transaction
- [x] Integer paise amounts backed by BigInteger
- [x] Password hashing (Argon2) and JWT access tokens
- [x] Registration/login, current-user authorization dependency
- [x] Seeded default income and expense categories at registration
- [x] Category list/create APIs
- [x] Account create/list/get/update APIs
- [x] Account balance endpoint
- [x] Transaction create/list/detail endpoints
- [x] Transaction summary (income, expense, net cash flow)
- [x] Account/category ownership checks and account-currency validation
- [x] CI configured with PostgreSQL, Alembic migration, and pytest
- [x] Test files added for health, auth, money invariants, and finance APIs

## API routes
- `GET /api/v1/health`, `GET /api/v1/ready`
- `POST /api/v1/auth/register`, `POST /api/v1/auth/login`
- `GET/POST /api/v1/categories`
- `GET/POST /api/v1/accounts`
- `GET/PATCH /api/v1/accounts/{account_id}`
- `GET /api/v1/accounts/{account_id}/balance`
- `GET/POST /api/v1/transactions`
- `GET /api/v1/transactions/{transaction_id}`
- `GET /api/v1/transactions/summary`

## Latest increment (2026-11-08)
- Added regression coverage proving another user's account, balance, transaction detail, and transaction list are not exposed.
- Test commit: `1141cb3d4fc8b7a92e0d760b86c4c247ede24bd4`
- The test is committed but has not been executed locally or confirmed green in GitHub Actions.

## Verification
- [x] CI workflow includes PostgreSQL service and migration step
- [x] Source files committed and selected files verified from GitHub
- [ ] GitHub Actions green run confirmed
- [ ] Local test run confirmed

Tests have not been executed from this environment because the runtime cannot resolve GitHub / install dependencies. Do not treat this code as production-ready until CI passes and a security review is completed.

## Still remaining in Phase 1
- [ ] Verify/fix CI failures
- [ ] Transaction update/reversal with audit trail
- [ ] Category update/deactivation
- [x] Cross-user authorization regression tests added (CI execution pending)
- [ ] API pagination/validation consistency
- [ ] Rate limiting and registration abuse prevention
- [ ] Token refresh/revocation/session strategy
- [ ] PR review before merging to main

## Finance invariants
- Integer paise only; never binary float.
- Positive amount magnitude; income adds, expense subtracts.
- Summaries filter currency; never combine different currencies.
- All financial endpoints require authenticated user scope.
- Transfer, loan, repayment, refund semantics are not implemented yet.
