import pytest
from httpx import AsyncClient, ASGITransport
from fastapi_jwt_auth import AuthJWT
from main import app
from models import User
from database import session, engine
from sqlalchemy.orm import sessionmaker


import random
import string

def generate_random_username():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def test_db():
    db = TestSessionLocal()
    yield db
    db.close()

@pytest.fixture(scope="module")
def test_user(test_db):
    if not test_db.query(User).filter(User.username == "testuser").first():
        user = User(username="testuser", password="hashedpassword")
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
    else:
        user = test_db.query(User).filter(User.username == "testuser").first()
    return user


def auth_token(test_user):
    authorize = AuthJWT()
    access_token = authorize.create_access_token(subject=test_user.username)
    return access_token


@pytest.mark.asyncio
async def test_get_user_settings(test_user):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(
            '/api/settings/',
            headers={'Authorization': f"Bearer {auth_token(test_user)}"}
        )
        assert response.status_code == 200
        assert response.json()['status'] == 'success'
        assert 'currency' in response.json()['data']


@pytest.mark.asyncio
async def test_update_user_settings(test_user):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.put(
            '/api/settings/update/',
            json={
                "currency": "USD",
                "reminder_enabled": True,
                "reminder_time": "10:00"
            },
            headers={'Authorization': f"Bearer {auth_token(test_user)}"},
        )

        assert response.status_code == 200 
        assert response.json()['currency'] == 'USD'
        assert response.json()['reminder_enabled'] == True
        assert response.json()['reminder_time'] == '10:00'


