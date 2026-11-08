# PaisaDiary — Product Blueprint
**Version:** 1.0  
**Product tagline:** *Har paise ka hisaab. Hamesha yaad.*  
**Status:** Product blueprint / foundation specification

---

## 1. Product Vision

PaisaDiary is an AI-powered personal finance assistant that helps users record, understand, manage, and remember every rupee across their financial life.

It is more than an expense tracker. It combines:
- Income and expense tracking
- Cash, bank, UPI, and wallet accounts
- Budgets and savings goals
- Loans and *udhaar* tracking
- Financial history and searchable memory
- AI-powered transaction understanding
- Reports, analytics, and financial insights
- Natural-language questions answered from the user's actual financial records

### Core promise

A user should be able to enter a transaction in one short sentence and later retrieve accurate information about it by date, category, account, merchant, person, trip, or context.

### Product principles

1. **Fast capture:** Recording a transaction should take only a few seconds.
2. **Accuracy first:** Financial arithmetic and balances must be deterministic, not guessed by an LLM.
3. **AI assists; the user remains in control:** AI may interpret, categorize, and explain, but must not silently invent or alter financial records.
4. **Reliable financial memory:** Historical answers must be grounded in persisted transactions.
5. **Privacy by design:** Financial records are private and isolated per user.
6. **Auditability:** Corrections and important changes must be traceable.
7. **Simple UX:** The interface should feel approachable, uncluttered, and mobile-first.
8. **Progressive complexity:** Basic expense entry is easy; advanced financial features remain available without overwhelming new users.

---

## 2. Target Users

- Students managing pocket money, scholarships, and daily expenses
- Individuals tracking salary, spending, and savings
- Families managing shared or household finances
- Users tracking cash, bank accounts, UPI, and wallets
- People managing informal loans and repayments (*udhaar*)
- Users who want to ask questions about past financial activity in natural language

---

## 3. Main User Experience

### 3.1 Quick transaction entry

Examples:
- `Pani puri 20`
- `Pizza 250`
- `Petrol 500 cash`
- `Papa ne 20000 bheje`
- `Book 450 paid by UPI`
- `Rohit ko 1000 udhaar diya`
- `Salary 35000 HDFC me aayi`

The parser should extract information it can confidently identify:
- Amount
- Transaction type: expense, income, transfer, loan, repayment, or refund
- Description
- Category and subcategory
- Date and time
- Account/payment method
- Merchant or counterparty
- Notes, tags, trip, or event context

If required information is ambiguous, PaisaDiary should ask a short clarification instead of guessing.

### 3.2 Confirmation and editing

- Show a clear transaction preview when confidence is low or the action is consequential.
- Allow the user to correct category, amount, date, account, or transaction type.
- Do not silently overwrite an existing transaction.
- Provide an undo or reversal workflow where appropriate.

### 3.3 Financial history and memory

Users should be able to search and retrieve transactions by:
- Day, date range, week, month, or year
- Category or subcategory
- Merchant or description
- Account or payment method
- Person/counterparty
- Trip, event, or tag
- Amount range
- Income, expense, transfer, loan, repayment, or refund

Example questions:
- “Last month food par kitna kharch hua?”
- “Papa ne ₹20,000 bheje the, usme se kitna spend hua?”
- “Pichhle saal books par kitna kharch kiya?”
- “Patna trip ka total expense batao.”
- “Rohit se kitna udhaar lena baaki hai?”

Answers must be based on the database and clearly indicate the relevant period and calculation.

---

## 4. Functional Modules

### 4.1 Dashboard
- Current balance by account
- Total income and expenses for selected period
- Net cash flow
- Budget progress
- Savings-goal progress
- Recent transactions
- Spending category breakdown
- Quick-add transaction entry
- Period selector: today, week, month, custom range

### 4.2 Smart Expense and Income Entry
- Natural-language entry
- Manual form entry
- AI parsing
- Rule-based categorization
- Category suggestions
- Account/payment-method selection
- Transaction editing and deletion/reversal
- Recurring transaction support (later phase)

### 4.3 Categories and Tags

Initial expense categories:
- Food & Dining
- Groceries
- Transport
- Fuel
- Health
- Shopping
- Education
- Bills & Utilities
- Rent & Housing
- Entertainment
- Travel
- Personal Care
- Gifts & Donations
- Other

Initial income categories:
- Salary
- Scholarship
- Freelance
- Business
- Interest
- Gift
- Refund
- Other

Users should eventually be able to create custom categories, subcategories, and tags.

### 4.4 Accounts and Balances

Supported account types:
- Cash
- Bank account
- UPI-linked account
- Wallet
- Credit card (future support)
- Other

Features:
- Opening balance
- Current balance
- Transaction history by account
- Account-to-account transfers
- Reconciliation and balance adjustment
- Account-specific reports

### 4.5 Budgets
- Monthly and custom-period budgets
- Category-level budgets
- Overall spending limit
- Spent / remaining / percentage used
- Alerts when approaching or exceeding a limit
- Budget history and comparison

### 4.6 Savings Goals
- Goal name
- Target amount
- Target date
- Current progress
- Contributions
- Remaining amount
- Goal status and progress visualization

### 4.7 Loans and Udhaar

Track money:
- Lent to another person
- Borrowed from another person
- Partially repaid
- Fully repaid

Each loan/udhaar record should support:
- Person/counterparty
- Principal amount
- Date
- Due date (optional)
- Repayment history
- Remaining balance
- Notes and status

Loan principal must not be classified as ordinary income or expense. Repayments must be recorded with correct accounting semantics.

### 4.8 Trips and Events
- Create a trip or event
- Associate transactions with it
- Track total expense
- Breakdown by category/person
- Shared expense tracking (later phase)
- Trip report and export

### 4.9 AI Financial Assistant

The assistant should answer questions such as:
- “Is month kitna kharch hua?”
- “Food expenses pichhle month se kitne badhe?”
- “Mere paas cash kitna bacha hai?”
- “Papa se aaye paise ka breakdown do.”
- “Mere pending loans ka total kya hai?”

Requirements:
- Query actual user-authorized records.
- Use deterministic calculation/query logic for totals and balances.
- Cite or show the date range and records/summary behind important answers.
- Clearly state when data is missing or ambiguous.
- Never fabricate transactions, balances, or financial facts.
- Never execute financial record changes without clear user intent and appropriate confirmation.

### 4.10 Reports and Export
- Daily, weekly, monthly, yearly reports
- Income vs expense
- Category-wise analysis
- Account-wise reports
- Budget reports
- Loan/udhaar reports
- Trip/event reports
- CSV, Excel, and PDF export

### 4.11 Future Capabilities
- Voice transaction entry
- Receipt OCR
- Bank statement import
- CSV import
- Recurring transactions
- Smart reminders
- Shared/family finance
- Bank/UPI integrations, where supported and authorized
- Multi-currency support
- Advanced forecasting and insights

---

## 5. Financial Correctness and Ledger Rules

These rules are mandatory:

1. Never use binary floating-point values for money.
2. Store money as integer minor units (e.g., paise) or an exact decimal type.
3. Use a consistent currency per transaction; default currency may be INR.
4. An account transfer is **not** income or expense.
5. Loan principal is **not** ordinary income or expense.
6. Refunds must be represented distinctly or linked to the original transaction.
7. Transaction edits/deletions must be auditable; use reversal records where appropriate.
8. Every balance must be derived from persisted, valid ledger entries or reconciled snapshots.
9. Prevent duplicate imports using stable identifiers and deduplication rules.
10. Use database transactions for multi-step financial operations.
11. Validate account ownership and user authorization on every operation.
12. AI must not independently determine authoritative balances or financial totals.
13. Use timezone-aware timestamps and preserve transaction date semantics.
14. Define rounding and currency precision explicitly.

---

## 6. Security, Privacy, and Trust

- Secure authentication and session handling
- User-level data isolation
- Authorization checks on every financial resource
- HTTPS in production
- Secrets stored in environment variables or a secret manager
- Password hashing using a suitable secure algorithm if passwords are managed directly
- Sensitive data minimization
- Encryption at rest where available and appropriate
- Audit logs for important financial changes
- Rate limiting and abuse protection
- Input validation and output encoding
- Safe file upload handling for receipts/statements
- Explicit consent and disclosure for sending financial data to external AI providers
- Never log secrets or unnecessary sensitive financial details
- Account export and user-controlled deletion workflows, subject to legal and audit requirements

---

## 7. Proposed Technology Stack

### Frontend
- **Web:** Next.js + TypeScript
- **Mobile:** React Native + Expo
- UI styling/component system: Tailwind-based web UI and a consistent mobile design system
- Data fetching and form validation: choose libraries based on repository conventions

### Backend
- Python
- FastAPI
- Pydantic for request/response validation
- SQLAlchemy
- Alembic migrations

### Database and infrastructure
- PostgreSQL as the primary database
- Redis optional for caching, queues, or rate limiting when justified
- Docker Compose for local development
- Object storage for receipts and attachments when needed

### AI layer
- LLM-based natural-language transaction parser
- Deterministic parsing/rules fallback
- Structured output schema and validation
- AI categorization with confidence score
- Retrieval/query layer grounded in the user's own database

**Architecture rule:** Keep AI provider/model integrations behind an abstraction so providers can be swapped without rewriting core financial logic.

---

## 8. High-Level Architecture

```text
Web / Mobile Client
        |
        v
API Gateway / FastAPI
        |
        +-- Authentication & Authorization
        |
        +-- Transaction Service
        |      +-- Ledger / Accounting Rules
        |      +-- Category Service
        |      +-- Account & Balance Service
        |
        +-- Budget & Savings Service
        |
        +-- Loan / Udhaar Service
        |
        +-- Trip / Event Service
        |
        +-- Reports & Analytics Service
        |
        +-- AI Assistant Service
        |      +-- Intent / Entity Parser
        |      +-- Structured Output Validation
        |      +-- Financial Query Planner
        |      +-- Database-grounded Answering
        |
        v
PostgreSQL
        |
        +-- Optional Redis / Queue
        +-- Optional Receipt/Object Storage
```

Core finance services should remain independent from AI-provider-specific code.

---

## 9. Initial Database Design

| Table / Entity | Purpose |
|---|---|
| `users` | User identity and preferences |
| `accounts` | Cash, bank, wallet, and other accounts |
| `transactions` | Income, expense, transfer, refund, and related entries |
| `categories` | Categories and subcategories |
| `tags` | User-defined labels |
| `transaction_tags` | Transaction/tag relationship |
| `budgets` | Budget definitions |
| `savings_goals` | Savings targets |
| `loans` | Borrowed/lent principal and status |
| `loan_repayments` | Repayment records |
| `trips` | Trip/event grouping |
| `trip_transactions` | Trip/transaction relationship |
| `recurring_transactions` | Recurring transaction rules |
| `attachments` | Receipt and document metadata |
| `audit_logs` | Traceable important changes |

### Database design considerations

- Use UUIDs or another non-guessable identifier strategy for public-facing resources.
- Include `user_id` ownership where appropriate.
- Add indexes for common filters: user, date, account, category, transaction type.
- Use foreign keys and database constraints.
- Use migrations for every schema change.
- Design transfers and loans with explicit transaction semantics.
- Consider a proper double-entry ledger if complex accounting is introduced; the first version must still maintain auditable and internally consistent account movements.

---

## 10. API Surface (Initial)

These are proposed endpoints; finalize them during API design.

### Authentication
- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh`
- `POST /auth/logout`

### Accounts
- `GET /accounts`
- `POST /accounts`
- `GET /accounts/{account_id}`
- `PATCH /accounts/{account_id}`
- `GET /accounts/{account_id}/balance`

### Transactions
- `GET /transactions`
- `POST /transactions`
- `POST /transactions/parse`
- `GET /transactions/{transaction_id}`
- `PATCH /transactions/{transaction_id}`
- `POST /transactions/{transaction_id}/reverse`
- `GET /transactions/summary`

### Categories
- `GET /categories`
- `POST /categories`
- `PATCH /categories/{category_id}`

### Budgets and savings
- `GET /budgets`
- `POST /budgets`
- `GET /savings-goals`
- `POST /savings-goals`

### Loans
- `GET /loans`
- `POST /loans`
- `POST /loans/{loan_id}/repayments`

### Assistant and reports
- `POST /assistant/query`
- `GET /reports/summary`
- `GET /reports/categories`
- `GET /reports/cashflow`
- `GET /exports/transactions`

All endpoints must enforce authentication, ownership, validation, and appropriate audit behavior.

---

## 11. Roadmap

### Phase 1 — Financial Foundation
- Repository and project structure
- Backend scaffold
- Configuration and environment management
- Database connection and migrations
- User/authentication foundation
- Accounts
- Transaction model and core ledger rules
- Income and expense CRUD
- Category management
- Basic balance calculations
- Initial dashboard/API summaries
- Unit and integration tests

### Phase 2 — AI Transaction Parsing
- Natural-language parser
- Structured parser output
- Category suggestions
- Confidence scoring
- Clarification flow for ambiguous input
- Deterministic fallback
- Parser evaluation tests

### Phase 3 — Core Finance Features
- Transfers
- Budgets
- Savings goals
- Loans and udhaar
- Repayments
- Account reconciliation

### Phase 4 — Financial Memory and Search
- Transaction search and filters
- Date/category/person/account queries
- Trips and events
- Reports
- CSV/Excel/PDF export

### Phase 5 — AI Financial Assistant
- Natural-language question answering
- Database-grounded query planning
- Deterministic totals
- Context-aware explanations
- Guardrails against hallucinated financial data

### Phase 6 — Advanced Input and Integrations
- Voice entry
- Receipt OCR
- Statement import
- Recurring transactions
- Reminders
- Additional integrations

### Phase 7 — Production Readiness
- Security review
- Performance testing
- Backup and recovery
- Monitoring and observability
- Accessibility
- Deployment and operational documentation
- Privacy and data-retention review

---

## 12. MVP Acceptance Criteria

The MVP is acceptable when:
- A user can securely sign in.
- A user can create and manage accounts.
- A user can record income and expenses quickly.
- Transactions have correct amount, date, type, category, and account.
- Transaction corrections are safe and auditable.
- Transfers do not inflate income or expenses.
- Account balances are calculated correctly.
- Transaction history can be filtered and searched.
- Monthly income, expense, and cash-flow summaries are accurate.
- AI parsing can interpret common short transaction phrases and ask for clarification when needed.
- AI assistant answers are grounded in actual stored records.
- User A cannot access User B's financial data.
- Automated tests cover financial rules, authorization, and key API behavior.

---

## 13. Quality Strategy

### Testing layers
- Unit tests for money arithmetic, categorization, parsing, and ledger rules
- API integration tests
- Database migration tests
- Authorization and user-isolation tests
- AI parser fixture/evaluation tests
- Regression tests for transfers, refunds, loans, and repayments
- End-to-end tests for primary user flows

### Important edge cases
- Zero or negative amounts where disallowed
- Duplicate transactions
- Incorrect dates/timezones
- Missing account
- Ambiguous transaction type
- Partial loan repayment
- Refund after original expense
- Transfer between two accounts
- Account balance reconciliation
- Concurrent transaction writes
- Importing the same statement twice
- AI hallucination or low-confidence extraction

---

## 14. UI/UX Direction

- Mobile-first
- Minimal, premium, uncluttered interface
- Fast transaction entry is the primary interaction
- Clear typography and high contrast
- Accessible labels and touch targets
- Light and dark themes
- Consistent spacing and component design
- Avoid unnecessary charts on the main screen
- Show important information at a glance
- Use progressive disclosure for advanced finance tools
- Support Hindi/Hinglish-friendly transaction entry; localization can expand later

---

## 15. Implementation Operating Rules

1. Inspect the existing repository before changing files.
2. Keep work on feature branches; do not directly modify `main`.
3. Build in small, reviewable increments.
4. Use migrations rather than manually changing production schema.
5. Add tests alongside financial logic.
6. Never claim tests passed unless they were actually run.
7. Never expose secrets in source code or logs.
8. Avoid unnecessary dependencies and heavy local workloads.
9. Keep the code modular, maintainable, and documented.
10. Complete the Phase 1 foundation before expanding into unrelated features.
11. Record architectural decisions and API/schema changes in documentation.
12. Preserve the product vision: **PaisaDiary is a financial assistant with reliable memory, not merely a CRUD expense tracker.**

---

## 16. Immediate Next Step

Start **Phase 1 — Financial Foundation** on the feature branch:

`feat/phase-1-foundation`

First inspect the repository, then define the backend structure, configuration, database schema, migration strategy, account model, transaction model, and financial invariants. Implement and test the foundation before adding AI features.

---

**Canonical product name:** PaisaDiary  
**Tagline:** Har paise ka hisaab. Hamesha yaad.
