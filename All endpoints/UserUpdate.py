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

#This endpoint need to be used with a user connected (endpoint /connect)
                
# Endpoint : /user/update
# Type : POST
# this endpoint modify informations of the user selected.
@app.post("/user/update", response_model = tuple)
async def update_user(user : UserModify):
    global user_jwt
    if user_jwt == None:
        raise HTTPException(status_code=401, detail="Please connect first")
    decoded_jwt = jwt.decode(user_jwt, SECRET_KEY, algorithms=["HS256"])
    user_role = decoded_jwt["role"]
    token = decoded_jwt["token"]    

    if user_role == "admin":
        query = text("UPDATE utilisateurs SET email = :email, firstname = :firstname, lastname = :lastname, birthdaydate = :birthdaydate, address = :address, postalcode = :postal, age = :age, meta = :meta, registrationdate = :registrationdate, role = :role WHERE id = :id RETURNING *")
    elif user_role == "user":
        query = text("UPDATE utilisateurs SET email = :email, birthdaydate = :birthdaydate, address = :address, postalcode = :postal, age = :age, meta = :meta, registrationdate = :registrationdate WHERE token = :token RETURNING *")
    values = {
        "id" : user.id,
        "token" : token,
        "email": user.email,
        "firstname": user.firstname,
        "lastname": user.lastname,
        "birthdaydate": user.birthday_date,
        "address" : user.address,
        "postal" : user.postal_code,
        "age": user.age,
        "meta" : user.meta,
        "registrationdate" : user.registration_date,
        "role" : user.role
    }
    with engine.begin() as conn:
            resultat = conn.execute(query, values).fetchone()
            query = text("SELECT email, password, role, id FROM utilisateurs WHERE email = :email")
            result_jwt = conn.execute(query, values).fetchone()
            encoded_jwt = jwt.encode({"email": result_jwt[0], "role":result_jwt[2]}, SECRET_KEY, algorithm="HS256")

            user_jwt = encoded_jwt
            return resultat
