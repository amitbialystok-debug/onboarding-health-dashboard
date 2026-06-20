# pytest tests for the accounts API endpoints

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base, get_db
from backend.main import app

TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)


SAMPLE_ACCOUNT = {
    "company_name": "Test Corp",
    "industry": "Technology",
    "contract_start_date": "2024-01-15",
    "seats_purchased": 100,
    "seats_active": 85,
    "logins_last_30_days": 320,
    "support_tickets_open": 4,
    "nps_score": 8,
}


def test_create_account(client):
    response = client.post("/api/v1/accounts", json=SAMPLE_ACCOUNT)
    assert response.status_code == 201
    data = response.json()
    assert data["company_name"] == "Test Corp"
    assert "id" in data


def test_get_accounts_empty(client):
    response = client.get("/api/v1/accounts")
    assert response.status_code == 200
    assert response.json() == []


def test_get_accounts_returns_created(client):
    client.post("/api/v1/accounts", json=SAMPLE_ACCOUNT)
    response = client.get("/api/v1/accounts")
    assert response.status_code == 200
    accounts = response.json()
    assert len(accounts) == 1
    assert accounts[0]["company_name"] == "Test Corp"


def test_get_single_account(client):
    created = client.post("/api/v1/accounts", json=SAMPLE_ACCOUNT).json()
    account_id = created["id"]
    response = client.get(f"/api/v1/accounts/{account_id}")
    assert response.status_code == 200
    assert response.json()["company_name"] == "Test Corp"


def test_get_missing_account(client):
    response = client.get("/api/v1/accounts/9999")
    assert response.status_code == 404


def test_health_score_included(client):
    created = client.post("/api/v1/accounts", json=SAMPLE_ACCOUNT).json()
    account_id = created["id"]
    response = client.get(f"/api/v1/accounts/{account_id}")
    assert response.status_code == 200
    data = response.json()
    assert "health" in data
    health = data["health"]
    assert "score" in health
    assert "risk_level" in health
    assert "signals" in health
    assert isinstance(health["score"], int)
    assert isinstance(health["signals"], list)
