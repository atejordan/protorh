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

class UserConnect (BaseModel):
    email : str
    password : str

app = FastAPI()

# Endpoint : /connect
# Type : POST
# this endpoint return a JWT token if the correct email and password are given.
@app.post("/connect", response_model=None)
async def user_connect(user : UserConnect):
    query = text("SELECT email, password, role, id, token FROM utilisateurs WHERE email = :email")
    password_salt = user.password + salt
    password = hashlib.md5(password_salt.encode('utf-8')).hexdigest()
    values = {
        "email": user.email
    }
    with engine.begin() as conn:
            result = conn.execute(query, values).fetchone()
            if result[1] != password:
                raise HTTPException(status_code=401, detail="Error Password")
            else:
                encoded_jwt = jwt.encode({"token": result[4], "role":result[2]}, SECRET_KEY, algorithm="HS256")
                global user_jwt
                user_jwt = encoded_jwt
                return encoded_jwt
