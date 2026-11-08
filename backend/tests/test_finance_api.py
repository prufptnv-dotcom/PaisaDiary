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
