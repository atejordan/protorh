import subprocess, uvicorn, hashlib, datetime, jwt
from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Float, text, ForeignKey, Date, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import database_exists, create_database
from pydantic import BaseModel
from decouple import Config, Csv, RepositoryEnv


today_year = datetime.date.today().year

config = Config(RepositoryEnv('/home/nicocaramel/protorh/protorh.env'))


salt = config.get('salt')
SECRET_KEY = config.get('SECRET_KEY')
DATABASE_HOST = config.get('DATABASE_HOST')
DATABASE_PORT = config.get('DATABASE_PORT')
DATABASE_NAME = config.get('DATABASE_NAME')
DATABASE_USER = config.get('DATABASE_USER')
DATABASE_PASSWORD = config.get('DATABASE_PASSWORD')

def hash_djb2(s):                                                                                                                                
    hash = 5381
    for x in s:
        hash = (( hash << 5) + hash) + ord(x)
    return hash & 0xFFFFFFFF


DATABASE_URL = "postgresql://nicocaramel:password@localhost/protorhapi"

engine = create_engine(DATABASE_URL)
if not database_exists(engine.url):
    create_database(engine.url, template="template0")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "utilisateurs"

    id = Column(Integer, primary_key=True, index=True)
    mail = Column(String)
    password = Column(String)
    firstname = Column(String)
    lastname = Column(String)
    birthday_date = Column(Date)
    address = Column(String)
    postal_code = Column(String)
    Age = Column(Integer)
    Meta = Column(String)
    RegistrationDate = Column(Date)
    Token=Column(String)
    Role = Column(String)

class UserCreate (BaseModel):
    email : str
    password : str
    repeat_password : str
    firstname : str
    lastname : str
    birthday_date : str
    address : str
    postal_code : str

app = FastAPI()

# Endpoint : /user/create
# Type : POST
# this endpoint add a user to the table User
@app.post("/user/create", response_model=tuple)
async def createuser(user : UserCreate):
    query = text("INSERT INTO utilisateurs VALUES (DEFAULT, :email, :password, :firstname, :lastname, :birthday_date, :address, :postal_code, :age, '{}', CURRENT_DATE::date, :token, 'user') RETURNING *")
    password_salt = user.password + salt
    password = hashlib.md5(password_salt.encode('utf-8')).hexdigest()

    repeatpassword_salt = user.repeat_password + salt
    repeat_password = hashlib.md5(repeatpassword_salt.encode('utf-8')).hexdigest()

    token_raw = user.email + user.firstname + user.lastname + salt
    token = hex(hash_djb2(token_raw))
    
    values = {
        "email" : user.email,
        "password" : password,
        "repeat_password" : repeat_password,
        "firstname" : user.firstname,
        "lastname" : user.lastname,
        "birthday_date" : user.birthday_date,
        "age" : today_year - int(user.birthday_date[:4]),
        "address" : user.address,
        "postal_code" : user.postal_code,
        "token" : token
    }
    if values["password"] != values["repeat_password"]:
        raise HTTPException(status_code=401, detail="Error Password")
    else:
        with engine.begin() as conn:
            result = conn.execute(query, values)
            
            return result.fetchone()
