import subprocess, uvicorn, hashlib, datetime, jwt
from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Float, text, ForeignKey, Date, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import database_exists, create_database
from pydantic import BaseModel
from decouple import Config, Csv, RepositoryEnv

config = Config(RepositoryEnv('/home/vboxuser/Desktop/api/protorh.env'))

user_jwt = None
salt = config.get('salt')
SECRET_KEY = config.get('SECRET_KEY')
DATABASE_HOST = config.get('DATABASE_HOST')
DATABASE_PORT = config.get('DATABASE_PORT')
DATABASE_NAME = config.get('DATABASE_NAME')
DATABASE_USER = config.get('DATABASE_USER')
DATABASE_PASSWORD = config.get('DATABASE_PASSWORD')

DATABASE_URL = "postgresql://jordan:jordan@localhost/mydatabase"

engine = create_engine(DATABASE_URL)
if not database_exists(engine.url):
    create_database(engine.url, template="template0")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class UserChange (BaseModel):
    email : str
    password : str
    new_password : str
    repeat_new_password : str

app = FastAPI()



@app.post("/user/password", response_model=str)
async def reset_password(user: UserChange):
   
    password_salt = user.password + salt
    password = hashlib.md5(password_salt.encode('utf-8')).hexdigest()

    newpassword_salt = user.new_password + salt
    new_password = hashlib.md5(newpassword_salt.encode('utf-8')).hexdigest()

    repeatnewpassword_salt = user.repeat_new_password + salt
    repeat_new_password = hashlib.md5(repeatnewpassword_salt.encode('utf-8')).hexdigest()


    values = {
        "email": user.email,
        "new_password": new_password
    }

    with engine.begin() as conn:
        query = text("SELECT password FROM utilisateurs WHERE email = :email")
        check_password = conn.execute(query, values).fetchone()
              
        if check_password[0] != password:                                           #check is the password given is correct
            raise HTTPException(status_code=401, detail="Error Password")
        if new_password != repeat_new_password:                                  #check if new password and repeat new password are the same
            raise HTTPExcepction(status_code=401, detail="Error Password")
        else:
            query = text("UPDATE utilisateurs SET password = :new_password WHERE email = :email RETURNING *")
            pass_check_password = conn.execute(query, values).fetchone()
        return "The password has been modified !"
   
