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
- [x] Category list/create/update/deactivate APIs
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
- Implemented transaction edit (`PATCH /transactions/{id}`), reversal (`POST /transactions/{id}/reverse`), and audit history (`GET /transactions/{id}/audit`).
- Added immutable event snapshots for create/update/reversal, reason capture for reversals, self-link metadata on reversal transactions, and Alembic migration `0002_transaction_audit`.
- Reversal posts a compensating transaction with the opposite type; it does not delete the original. Reversed entries cannot be edited/reversed again.
- Added tests for edit → reversal balance neutrality, audit snapshots, duplicate reversal conflict, and cross-user reversal/audit access.
- Added PATCH category endpoint for user-scoped rename and active/inactive toggling; duplicate category names are rejected within user+kind.
- Transaction creation now rejects inactive categories; historical transactions remain linked to the category.
- Added API tests for category rename/deactivation, inactive-category assignment rejection, and duplicate-name conflict.
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
- [x] Transaction update/reversal with audit trail (CI execution pending)
- [x] Category update/deactivation (CI execution pending)
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
