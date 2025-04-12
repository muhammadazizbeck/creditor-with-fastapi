from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base,sessionmaker

DATABASE_URL='postgresql://postgres:Azizbek1410@localhost/creditor_db'

engine = create_engine(DATABASE_URL,echo=True)

Base = declarative_base()
session = sessionmaker()



