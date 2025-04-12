from fastapi import APIRouter, status, HTTPException, Depends,Query
from schemas import SettingModel
from fastapi_jwt_auth import AuthJWT
from models import User,Setting
from database import session, engine
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder

settings_router = APIRouter(
    prefix='/api/settings'
)

session = session(bind=engine)

@settings_router.get('/', status_code=status.HTTP_200_OK)
async def get_user_settings(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()  
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f'Please enter valid access token! Error: {str(e)}'
        )
    current_user = Authorize.get_jwt_subject()

    user = session.query(User).filter(User.username == current_user).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User not found'
        )

    settings = session.query(Setting).filter(Setting.user_id == user.id).first()

    if not settings:
        settings = Setting(user_id=user.id)
        session.add(settings)
        session.commit()
        session.refresh(settings)

    data = {
        'currency': settings.currency,
        'reminder_enabled': settings.reminder_enabled,
        'reminder_time': settings.reminder_time
    }

    return jsonable_encoder({
        'status': 'success',
        'code': 200,
        'data': data
    })

from fastapi.encoders import jsonable_encoder

@settings_router.put('/update', status_code=status.HTTP_200_OK)
async def update_user_settings(update_model: SettingModel, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Iltimos, haqiqiy kirish tokenini kiriting!')

    current_user = Authorize.get_jwt_subject() 
    user = session.query(User).filter(User.username == current_user).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Foydalanuvchi topilmadi')

    settings = session.query(Setting).filter(Setting.user_id == user.id).first()

    if not settings:
        settings = Setting(user_id=user.id)
        session.add(settings)

    if update_model.currency is not None:
        settings.currency = update_model.currency

    if update_model.reminder_enabled is not None:
        settings.reminder_enabled = update_model.reminder_enabled

    if update_model.reminder_time is not None:
        settings.reminder_time = update_model.reminder_time

    session.commit()
    session.refresh(settings)

    return jsonable_encoder({
        'currency': settings.currency,
        'reminder_enabled': settings.reminder_enabled,
        'reminder_time': settings.reminder_time
    })



