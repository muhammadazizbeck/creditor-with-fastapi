from sqlalchemy import Column,Integer,String,Enum,Float,Text,DateTime,Boolean,ForeignKey
from sqlalchemy.orm import relationship
import enum
import datetime
from database import Base


class User(Base):
    __tablename__='users'
    id = Column(Integer,primary_key=True,index=True)
    username = Column(String(128),unique=True)
    email = Column(String(128),unique=True)
    password = Column(String(512))

    debts = relationship('Debt',back_populates='owner')
    settings = relationship('Setting',back_populates='user',uselist=False)

    def __repr__(self):
        return f"User:{self.username}"

class DebtType(str,enum.Enum):
    owed_to = 'owed_to'
    owed_by = 'owed_by'
    individual = 'individual'


class Debt(Base):
    __tablename__='debts'
    id = Column(Integer,primary_key=True,index=True)
    full_name = Column(String)
    amount = Column(Float)
    currency = Column(String(128))
    description = Column(Text)
    debt_type = Column(Enum(DebtType))

    given_date = Column(DateTime,default=datetime.datetime.utcnow)
    return_date = Column(DateTime)

    owner_id = Column(Integer,ForeignKey('users.id'))
    owner = relationship('User',back_populates='debts')

class Setting(Base):
    __tablename__='settings'
    id = Column(Integer, primary_key=True, index=True)
    currency = Column(String(128),default='UZS')
    reminder_enabled = Column(Boolean,default=True)
    reminder_time = Column(DateTime)

    user_id = Column(Integer,ForeignKey('users.id'))
    user = relationship('User',back_populates='settings')



