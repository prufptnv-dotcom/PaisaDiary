from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app

test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSession = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)
Base.metadata.create_all(bind=test_engine)


def override_get_db() -> Generator[Session, None, None]:
    session = TestSession()
    try:
        yield session
    finally:
        session.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_register_then_login() -> None:
    email = "vikash-test-auth@example.com"
    registration = client.post("/api/v1/auth/register", json={
        "email": email,
        "display_name": "Vikash Test",
        "password": "correct-horse-battery-2026",
    })
    assert registration.status_code == 201
    body = registration.json()
    assert body["token_type"] == "bearer"
    assert body["user"]["email"] == email
    assert body["access_token"]

    login = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": "correct-horse-battery-2026",
    })
    assert login.status_code == 200
    assert login.json()["access_token"]


def test_login_rejects_wrong_password() -> None:
    response = client.post("/api/v1/auth/login", json={
        "email": "vikash-test-auth@example.com",
        "password": "incorrect-password",
    })
    assert response.status_code == 401
