from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from models import DebtType


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


class MonitoringResponse(BaseModel):
    total_owed_to: float
    total_owed_by: float
    balance: float

class DebtCreate(BaseModel):
    full_name: str
    amount: float
    currency: str
    description: Optional[str] = None
    debt_type: DebtType
    return_date: Optional[datetime] = None

class DebtUpdate(BaseModel):
    full_name: Optional[str]
    amount: Optional[float]
    currency: Optional[str]
    description: Optional[str]
    debt_type: Optional[DebtType]
    return_date: Optional[datetime]

class DebtResponse(BaseModel):
    id: int
    full_name: str
    amount: float
    currency: str
    description: Optional[str]
    debt_type: DebtType
    given_date: datetime
    return_date: Optional[datetime]

    class Config:
        orm_mode = True


