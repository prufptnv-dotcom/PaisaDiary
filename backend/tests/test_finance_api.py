from collections.abc import Generator
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_current_user
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.user import User

engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
SessionTest = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base.metadata.create_all(bind=engine)


def override_db() -> Generator[Session, None, None]:
    db = SessionTest()
    try:
        yield db
    finally:
        db.close()


db = SessionTest()
test_user = User(
    id=uuid4(),
    email="finance-api-test@example.com",
    display_name="Finance API Test",
    password_hash="test-hash",
)
db.add(test_user)
db.commit()
db.refresh(test_user)


def override_user() -> User:
    return test_user


app.dependency_overrides[get_db] = override_db
app.dependency_overrides[get_current_user] = override_user
client = TestClient(app)


def test_account_and_transaction_balance_flow() -> None:
    account_response = client.post("/api/v1/accounts", json={
        "name": "Cash",
        "account_type": "cash",
        "opening_balance_paise": 100_000,
        "currency": "INR",
    })
    assert account_response.status_code == 201
    account_id = account_response.json()["id"]

    expense = client.post("/api/v1/transactions", json={
        "account_id": account_id,
        "transaction_type": "expense",
        "amount_paise": 12_500,
        "currency": "INR",
        "description": "Groceries",
    })
    assert expense.status_code == 201

    income = client.post("/api/v1/transactions", json={
        "account_id": account_id,
        "transaction_type": "income",
        "amount_paise": 50_000,
        "currency": "INR",
        "description": "Pocket money",
    })
    assert income.status_code == 201

    balance = client.get(f"/api/v1/accounts/{account_id}/balance")
    assert balance.status_code == 200
    assert balance.json()["balance_paise"] == 137_500


def test_accounts_are_user_scoped() -> None:
    # This user only sees records whose user_id matches the authenticated principal.
    response = client.get("/api/v1/accounts")
    assert response.status_code == 200
    assert all(account["name"] == "Cash" for account in response.json())


def test_cross_user_account_and_transaction_access_is_hidden() -> None:
    from app.models.account import Account, AccountType
    from app.models.transaction import Transaction, TransactionType

    other_user = User(
        id=uuid4(),
        email=f"other-{uuid4()}@example.com",
        display_name="Other User",
        password_hash="test-hash",
    )
    other_account = Account(
        id=uuid4(),
        user_id=other_user.id,
        name="Private Other Cash",
        account_type=AccountType.CASH,
        currency="INR",
        opening_balance_paise=90_000,
        is_active=True,
    )
    other_transaction = Transaction(
        id=uuid4(),
        user_id=other_user.id,
        account_id=other_account.id,
        transaction_type=TransactionType.EXPENSE,
        amount_paise=1_500,
        currency="INR",
        description="Private Other Transaction",
    )
    db.add_all([other_user, other_account, other_transaction])
    db.commit()

    # Account and balance endpoints must not reveal another user's records.
    assert client.get(f"/api/v1/accounts/{other_account.id}").status_code == 404
    assert client.get(f"/api/v1/accounts/{other_account.id}/balance").status_code == 404

    # Transaction detail must also be user-scoped.
    assert client.get(f"/api/v1/transactions/{other_transaction.id}").status_code == 404

    # Lists are scoped, even when a foreign account UUID is supplied as a filter.
    visible_accounts = client.get("/api/v1/accounts").json()
    assert all(item["id"] != str(other_account.id) for item in visible_accounts)

    visible_transactions = client.get("/api/v1/transactions").json()
    assert all(item["id"] != str(other_transaction.id) for item in visible_transactions)

    filtered_transactions = client.get(
        "/api/v1/transactions", params={"account_id": str(other_account.id)}
    ).json()
    assert filtered_transactions == []


def test_category_update_deactivation_and_inactive_assignment() -> None:
    category_response = client.post("/api/v1/categories", json={
        "name": "Temporary Category",
        "kind": "expense",
    })
    assert category_response.status_code == 201
    category_id = category_response.json()["id"]

    renamed = client.patch(f"/api/v1/categories/{category_id}", json={
        "name": "Updated Temporary Category",
    })
    assert renamed.status_code == 200
    assert renamed.json()["name"] == "Updated Temporary Category"

    deactivated = client.patch(f"/api/v1/categories/{category_id}", json={
        "is_active": False,
    })
    assert deactivated.status_code == 200
    assert deactivated.json()["is_active"] is False

    listed_ids = {item["id"] for item in client.get("/api/v1/categories").json()}
    assert category_id not in listed_ids

    account_response = client.post("/api/v1/accounts", json={
        "name": "Category Test Cash",
        "account_type": "cash",
        "opening_balance_paise": 0,
        "currency": "INR",
    })
    assert account_response.status_code == 201

    transaction_response = client.post("/api/v1/transactions", json={
        "account_id": account_response.json()["id"],
        "category_id": category_id,
        "transaction_type": "expense",
        "amount_paise": 100,
        "currency": "INR",
        "description": "Must not use inactive category",
    })
    assert transaction_response.status_code == 404


def test_category_update_rejects_duplicate_name() -> None:
    first = client.post("/api/v1/categories", json={
        "name": "Duplicate Candidate A",
        "kind": "expense",
    })
    second = client.post("/api/v1/categories", json={
        "name": "Duplicate Candidate B",
        "kind": "expense",
    })
    assert first.status_code == 201
    assert second.status_code == 201

    duplicate = client.patch(f"/api/v1/categories/{second.json()['id']}", json={
        "name": "Duplicate Candidate A",
    })
    assert duplicate.status_code == 409

def test_transaction_update_reversal_and_audit_history() -> None:
    account_response = client.post("/api/v1/accounts", json={
        "name": "Audit Flow Cash",
        "account_type": "cash",
        "opening_balance_paise": 0,
        "currency": "INR",
    })
    assert account_response.status_code == 201
    account_id = account_response.json()["id"]

    created = client.post("/api/v1/transactions", json={
        "account_id": account_id,
        "transaction_type": "income",
        "amount_paise": 20_000,
        "currency": "INR",
        "description": "Initial payment",
    })
    assert created.status_code == 201
    transaction_id = created.json()["id"]

    updated = client.patch(f"/api/v1/transactions/{transaction_id}", json={
        "amount_paise": 25_000,
        "description": "Corrected payment",
    })
    assert updated.status_code == 200
    assert updated.json()["amount_paise"] == 25_000
    assert updated.json()["description"] == "Corrected payment"

    balance_after_update = client.get(f"/api/v1/accounts/{account_id}/balance")
    assert balance_after_update.json()["balance_paise"] == 25_000

    reversal = client.post(f"/api/v1/transactions/{transaction_id}/reverse", json={
        "reason": "Entered income in error",
    })
    assert reversal.status_code == 201
    assert reversal.json()["transaction_type"] == "expense"
    assert reversal.json()["amount_paise"] == 25_000
    assert reversal.json()["reversal_of_id"] == transaction_id

    original = client.get(f"/api/v1/transactions/{transaction_id}")
    assert original.status_code == 200
    assert original.json()["is_reversed"] is True

    balance_after_reversal = client.get(f"/api/v1/accounts/{account_id}/balance")
    assert balance_after_reversal.json()["balance_paise"] == 0

    duplicate_reversal = client.post(f"/api/v1/transactions/{transaction_id}/reverse", json={
        "reason": "Trying to reverse again",
    })
    assert duplicate_reversal.status_code == 409

    audit = client.get(f"/api/v1/transactions/{transaction_id}/audit")
    assert audit.status_code == 200
    event_types = [item["event_type"] for item in audit.json()]
    assert event_types == ["created", "updated", "reversed"]
    assert audit.json()[1]["before_snapshot"]["amount_paise"] == 20_000
    assert audit.json()[1]["after_snapshot"]["amount_paise"] == 25_000


def test_reversal_and_audit_endpoints_are_user_scoped() -> None:
    from app.models.account import Account, AccountType
    from app.models.transaction import Transaction, TransactionType

    foreign_user = User(
        id=uuid4(), email=f"foreign-audit-{uuid4()}@example.com",
        display_name="Foreign Audit User", password_hash="test-hash",
    )
    foreign_account = Account(
        id=uuid4(), user_id=foreign_user.id, name="Foreign Account",
        account_type=AccountType.CASH, currency="INR",
        opening_balance_paise=0, is_active=True,
    )
    foreign_transaction = Transaction(
        id=uuid4(), user_id=foreign_user.id, account_id=foreign_account.id,
        transaction_type=TransactionType.INCOME, amount_paise=500,
        currency="INR", description="Foreign transaction",
    )
    db.add_all([foreign_user, foreign_account, foreign_transaction])
    db.commit()

    assert client.post(
        f"/api/v1/transactions/{foreign_transaction.id}/reverse",
        json={"reason": "Should be forbidden"},
    ).status_code == 404
    assert client.get(f"/api/v1/transactions/{foreign_transaction.id}/audit").status_code == 404

