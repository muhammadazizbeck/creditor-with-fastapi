import pytest
from httpx import AsyncClient
from main_routes.main import app
from fastapi_jwt_auth import AuthJWT
from models import User
from database import session,engine
from sqlalchemy.orm import sessionmaker

TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def test_db():
    db = TestSessionLocal()
    yield db
    db.close()

@pytest.fixture(scope="module")
def test_user(test_db):
    user = User(username="testuser", password="hashedpassword")
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


def auth_token(test_user):
    Authorize = AuthJWT()
    access_token = Authorize.create_access_token(subject=test_user.username)
    return access_token


@pytest.mark.asyncio
async def test_get_user_settings():
    async with AsyncClient(app=app,base_url="http://test") as ac:
        response = await ac.get(
            '/api/settings/',
            headers = {'Authorization':f"Bearer token {auth_token}"}
        )

        assert response.status_code == 200
        assert response['status'] == 'success'
        assert 'currency' in  response.json['data']
    
@pytest.mark.asyncio
async def test_update_user_settings():
    async with AsyncClient(app=app,base_url="http://test") as ac:
        response = await ac.put(
            '/api/settings/update/',
            json={
                "currency": "USD",
                "reminder_enabled": True,
                "reminder_time": "10:00"
            },
            headers={'Authorization':f"Bearer token {auth_token}"}
        )
        assert response.status_code == 200
        assert response.json['currency'] == 'USD'
        assert response.json['reminder_enabled'] == True
        assert response.json['reminder_time'] == '10:00'
