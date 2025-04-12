import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User, Base
from database import engine
from fastapi.testclient import TestClient
from main import app

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

client = TestClient(app)

def test_register(client, test_db):
    data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "newpassword123"
    }
    response = client.post("/api/auth/register", json=data)
    assert response.status_code == 201
    assert response.json()["message"] == "User is successfully signed up"
    assert response.json()["data"]["username"] == data["username"]

def test_register_existing_user(client, test_user):
    data = {
        "username": test_user.username,
        "email": "testuser@example.com",
        "password": "newpassword123"
    }
    response = client.post("/api/auth/register", json=data)
    assert response.status_code == 400
    assert response.json()["detail"] == "User with this username is already exists!"

def test_login(client, test_user):
    data = {
        "username_or_email": test_user.username,
        "password": "hashedpassword" 
    }
    response = client.post("/api/auth/login", json=data)
    assert response.status_code == 200
    assert "access_token" in response.json()["data"]
    assert "refresh_token" in response.json()["data"]

def test_login_invalid_credentials(client):
    data = {
        "username_or_email": "wronguser",
        "password": "wrongpassword"
    }
    response = client.post("/api/auth/login", json=data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Please enter a valid access token"

def test_login_missing_credentials(client):
    data = {
        "username_or_email": "",
        "password": ""
    }
    response = client.post("/api/auth/login", json=data)
    assert response.status_code == 422  
    assert "detail" in response.json()
