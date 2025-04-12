from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RegisterModel(BaseModel):
    username:str
    email:str
    password:str
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            'example':{
                'username':'noname',
                'email':'noname@gmail.com',
                'password':'nonamepass'
            }
        }

class Settings(BaseModel):
    authjwt_secret_key: str = "ea97da71bc7f4b4fbb743585badd3c346a62deeb0fe4db1e0cde1233aac031d1"
    authjwt_algorithm: str = "HS256"
    authjwt_access_token_expires: int = 60

class LoginModel(BaseModel):
    username_or_email:str
    password:str

    class Config:
        from_attributes = True
        json_schema_extra = {
            'example':{
                'username':'noname',
                'password':"nonamepass"
            }
        }

class SettingModel(BaseModel):
    currency:Optional[str]="UZS"
    reminder_enabled:Optional[bool]
    reminder_time:Optional[datetime]=None

    class Config:
        from_attributes = True


