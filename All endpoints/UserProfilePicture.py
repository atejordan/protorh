import subprocess, uvicorn, hashlib, datetime, jwt, os, shutil
from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Float, text, ForeignKey, Date, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import database_exists, create_database
from pydantic import BaseModel, dataclasses
from decouple import Config, Csv, RepositoryEnv
from PIL import Image


class UserPfp(BaseModel):
    img : str




app = FastAPI()


# Endpoint : /upload/picture/user/{user_id}
# Type : POST
# this endpoint upload a profile picture for a user.
@app.post("/upload/picture/user/{user_id}")
async def upload_profilepicture(user : UserPfp, user_id : int):
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



    correct_extensions = ["png", "jpg", "gif"]             #check if the picture has the good extension
    img_name = os.path.basename(user.img)
    if img_name.split(".")[1] not in correct_extensions:
        return {"type":"upload_error", "error":"uncorrect extension"}
    extension_used = img_name.split(".")[1]
    os.rename(user.img, f"{token[0]}.{extension_used}")
    shutil.copy(f"{token[0]}.{extension_used}", destination)

    return "Picture Uploaded !"
