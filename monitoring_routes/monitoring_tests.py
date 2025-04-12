import pytest
from fastapi.testclient import TestClient
from main import app 
from models import Base, engine, User, Debt, DebtType
from database import session as db_session
from werkzeug.security import generate_password_hash
from fastapi_jwt_auth import AuthJWT


client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_and_teardown():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def create_test_user_and_token():
    session = db_session(bind=engine)
    
    test_user = User(
        username="testuser",
        email="test@example.com",
        password=generate_password_hash("password123")
    )
    session.add(test_user)
    session.commit()

    debt1 = Debt(
        full_name="Ali",
        amount=1000.0,
        currency="USD",
        debt_type=DebtType.owed_to,
        owner_id=test_user.id
    )
    debt2 = Debt(
        full_name="Vali",
        amount=300.0,
        currency="USD",
        debt_type=DebtType.owed_by,
        owner_id=test_user.id
    )

    session.add_all([debt1, debt2])
    session.commit()

    access_token = AuthJWT.create_access_token(subject=test_user.username)

    return access_token

def test_monitoring_with_token():
    token = create_test_user_and_token()

    response = client.get(
        "/api/monitoring/",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json() == {
        "total_owed_to": 1000.0,
        "total_owed_by": 300.0,
        "balance": 700.0
    }

def test_monitoring_without_token():
    response = client.get("/api/monitoring/")
    assert response.status_code == 401
    assert response.json()["detail"] == "Token is invalid or missing"
