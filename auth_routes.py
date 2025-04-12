from fastapi import APIRouter,status,Depends
from schemas import RegisterModel,LoginModel
from models import User
from database import session,engine
from fastapi.exceptions import HTTPException
from fastapi.encoders import jsonable_encoder
from werkzeug.security import check_password_hash,generate_password_hash
from fastapi_jwt_auth import AuthJWT
from sqlalchemy import or_
import datetime


auth_router = APIRouter(
    prefix='/api/auth'
)

session = session(bind=engine)

@auth_router.get('/')
async def welcome():
    response = {
        'message':"Welcome our auth page"
    }
    return response

@auth_router.post('/register',status_code=status.HTTP_201_CREATED)
async def register(user:RegisterModel):
    username = session.query(User).filter(User.username==user.username).first()
    if username is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail='User with this username is already exists!')
    email = session.query(User).filter(User.email==user.email).first()
    if email is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="User with this email is already exists")
    
    new_user = User(
        username=user.username,
        email=user.email,
        password=generate_password_hash(user.password)
    )
    session.add(new_user)
    session.commit()

    data = {
        'username':new_user.username,
        'email':new_user.email,
        'password':new_user.password
    }

    response = {
        'status':'success',
        'code':201,
        'message':"User is successfully signed up",
        'data':data
    }
    return jsonable_encoder(response)

@auth_router.post('/login',status_code=status.HTTP_200_OK)
async def login(user:LoginModel,Authorize:AuthJWT=Depends()):
    access_token_lifetime = datetime.timedelta(minutes=60)
    refresh_token_lifetime = datetime.timedelta(days=15)
    db_user = session.query(User).filter(
        or_(User.username==user.username_or_email,
            User.email==user.username_or_email)
    ).first()
    if user and check_password_hash(db_user.password,user.password):
        access_token = Authorize.create_access_token(subject=db_user.username,expires_time=access_token_lifetime)
        refresh_token = Authorize.create_refresh_token(subject=db_user.username,expires_time=refresh_token_lifetime)

        tokens = {
            'access_token':access_token,
            'refresh_token':refresh_token
        }

        response = {
            'status':'success',
            'code':200,
            'message':'User is successfully logged in',
            'data':tokens
        }
        return jsonable_encoder(response)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Please enter a valid access token")
    


