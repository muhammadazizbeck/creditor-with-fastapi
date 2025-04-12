import pytest
from fastapi.testclient import TestClient
from main import app
from database import Base, engine, session as db_session
from models import User
from werkzeug.security import generate_password_hash
from fastapi_jwt_auth import AuthJWT
import datetime

client = TestClient(app)

@pytest.fixture(scope="module")
def test_db():
    Base.metadata.create_all(bind=engine)
    test_user = User(
        username="testuser",
        email="testuser@example.com",
        password=generate_password_hash("testpassword")
    )
    db = db_session(bind=engine)
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    yield test_user
    db.query(User).delete()
    db.commit()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def auth_headers(test_db):
    token = AuthJWT.create_access_token(subject=test_db.username)
    return {"Authorization": f"Bearer {token}"}


def test_create_debt(auth_headers):
    response = client.post(
        "/api/debts/",
        json={
            "full_name": "Ali",
            "amount": 100000,
            "currency": "UZS",
            "description": "Do‘stdan qarz",
            "debt_type": "owed_by",
            "return_date": "2025-05-01T00:00:00"
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    assert response.json()["full_name"] == "Ali"


def test_get_all_debts(auth_headers):
    response = client.get("/api/debts/", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1


def test_get_single_debt(auth_headers):
    debts = client.get("/api/debts/", headers=auth_headers).json()
    debt_id = debts[0]["id"]

    response = client.get(f"/api/debts/{debt_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == debt_id


def test_update_debt(auth_headers):
    debts = client.get("/api/debts/", headers=auth_headers).json()
    debt_id = debts[0]["id"]

    response = client.put(
        f"/api/debts/{debt_id}",
        json={
            "description": "Yangilangan ta'rif",
            "amount": 150000
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["amount"] == 150000
    assert response.json()["description"] == "Yangilangan ta'rif"


def test_delete_debt(auth_headers):
    debts = client.get("/api/debts/", headers=auth_headers).json()
    debt_id = debts[0]["id"]

    response = client.delete(f"/api/debts/{debt_id}", headers=auth_headers)
    assert response.status_code == 204

    response_check = client.get(f"/api/debts/{debt_id}", headers=auth_headers)
    assert response_check.status_code == 404
