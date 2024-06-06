import subprocess, uvicorn, hashlib, datetime, jwt, os, shutil
from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Float, text, ForeignKey, Date, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import database_exists, create_database
from pydantic import BaseModel, dataclasses
from decouple import Config, Csv, RepositoryEnv
from PIL import Image

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

class UserPfp(BaseModel):
    img : str


app = FastAPI()

# Endpoint : /picture/user/{user_id}
# Type : GET
# this endpoint get the picture from a user selected
@app.get("/picture/user/{user_id}")
async def get_user_picture(user_id : int):

    query = text("SELECT token FROM utilisateurs WHERE id = :user_id")      #get token
    values = {
        "user_id" : user_id
    }
    with engine.begin() as conn:
        token = conn.execute(query, values).fetchone()                 
    if token == None:                                                #if no token = not a valide user
        return {"type": "user_error", "error": "User not found"}
    
    destination = "/home/nicocaramel/protorh/assets/picture/profiles"      
    exsitant_files_destination = os.listdir(destination)                 #list all files in directory

    for i in range(len(exsitant_files_destination)):                  
        if exsitant_files_destination[i].split(".")[0] == token[0]:           #check for the correct picture 
            return exsitant_files_destination[i]
        
    return "/home/nicocaramel/protorh/assets/picture/profiles/pdp_base.png"      #if no picture find return classic pfp

