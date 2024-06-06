import subprocess, uvicorn, hashlib, datetime, jwt
from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Float, text, ForeignKey, Date, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import database_exists, create_database
from pydantic import BaseModel, dataclasses
from decouple import Config, Csv, RepositoryEnv


today_year = datetime.date.today().year





config = Config(RepositoryEnv('/home/nicocaramel/protorh/protorh.env'))




user_jwt = None
salt = config.get('salt')
SECRET_KEY = config.get('SECRET_KEY')
DATABASE_HOST = config.get('DATABASE_HOST')
DATABASE_PORT = config.get('DATABASE_PORT')
DATABASE_NAME = config.get('DATABASE_NAME')
DATABASE_USER = config.get('DATABASE_USER')
DATABASE_PASSWORD = config.get('DATABASE_PASSWORD')


DATABASE_URL = "postgresql://nicocaramel:password@localhost/protorhapi"

engine = create_engine(DATABASE_URL)
if not database_exists(engine.url):
    create_database(engine.url, template="template0")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()




class UserModify (BaseModel):
    id : str = None
    email : str
    firstname : str = None
    lastname : str = None
    birthday_date : str 
    address : str
    postal_code : str
    age : str
    meta : str 
    registration_date : str
    role: str = None



app = FastAPI()




# Endpoint : /user/{user_id}
# Type : GET
# this endpoint return informations on the user. The endpoint is accessible only if a correct JWT is given.
@app.get("/user/{user_id}", response_model = tuple)
async def user_getdata(user_id : int):
    if user_jwt == None:
        raise HTTPException(status_code=401, detail="Please connect first")
    else:
        decoded_jwt = jwt.decode(user_jwt, SECRET_KEY, algorithms=["HS256"])
        user_role = decoded_jwt["role"]
        if user_role == "user":
            query = text("SELECT email, firstname, lastname, age, registrationdate, role FROM utilisateurs WHERE id = :user_id")
        elif user_role == "admin":
            query = text("SELECT email, firstname, lastname, birthdaydate, address, postalcode, age, meta, registrationdate, token, role FROM utilisateurs WHERE id = :user_id")
        values = {
            "user_id" : user_id
        }
        with engine.begin() as conn:
            result = conn.execute(query, values).fetchone()
            return result

