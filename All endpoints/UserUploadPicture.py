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

# Endpoint : /upload/picture/user/{user_id}
# Type : POST
# this endpoint upload a profile picture for a user.
@app.post("/upload/picture/user/{user_id}")
async def upload_profilepicture(user : UserPfp, user_id : int):

    if not(os.path.isfile(user.img)):                                               #if picture send is not find return basic pfp
        return "/home/nicocaramel/protorh/assets/picture/profiles/pdp_base.png"

    query = text("SELECT token FROM utilisateurs WHERE id = :user_id")
    
    values = {
        "user_id" : user_id
    }
    with engine.begin() as conn:
        token = conn.execute(query, values).fetchone()                  #if user exist -> take his token
    if token == None:
        return {"type": "user_error", "error": "User not found"}
    
    destination = "/home/nicocaramel/protorh/assets/picture/profiles"       #check if the user already got a profile picture
    exsitant_files_destination = os.listdir(destination)
    for i in range(len(exsitant_files_destination)):
        if exsitant_files_destination[i].split(".")[0] == token[0]:
            return {"type":"upload_error", "error":"picture already exist"}

    picture = Image.open(user.img)                 #check the size of the picture to be 800*800 max
    width = picture.width
    height = picture.height
    if width > 800 or height > 800:
        return {"type":"upload_error", "error":"picture size is not correct"}



    correct_extensions = ["png", "jpg", "gif"]             
    img_name = os.path.basename(user.img)
    if img_name.split(".")[1] not in correct_extensions:                 #check if the picture has the good extension
        return {"type":"upload_error", "error":"uncorrect extension"}
    extension_used = img_name.split(".")[1]

    os.rename(user.img, f"{token[0]}.{extension_used}")                 #rename the picture with {token of user}.{extention of file} 
    shutil.copy(f"{token[0]}.{extension_used}", destination)            #move the picture to the good directory

    return "Picture Uploaded !"

