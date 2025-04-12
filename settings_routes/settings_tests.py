import pytest
from httpx import AsyncClient
from main import app
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

