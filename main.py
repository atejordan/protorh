import subprocess, uvicorn, hashlib, datetime, jwt, os, shutil
from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Float, text, ForeignKey, Date, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import database_exists, create_database
from pydantic import BaseModel, dataclasses
from decouple import Config, Csv, RepositoryEnv
from PIL import Image

today_year = datetime.date.today().year


config = Config(RepositoryEnv('/home/nicocaramel/protorh/protorh.env'))


user_jwt = None
salt = config.get('salt')
SECRET_KEY = config.get('SECRET_KEY')
DATABASE_HOST = config.get('DATABASE_HOST')
DATABASE_PORT = config.get('DATABASE_PORT')               #all env variable
DATABASE_NAME = config.get('DATABASE_NAME')
DATABASE_USER = config.get('DATABASE_USER')
DATABASE_PASSWORD = config.get('DATABASE_PASSWORD')


def hash_djb2(s):                                     #alg hash_djb2 for token creation                                                                                            
    hash = 5381
    for x in s:
        hash = (( hash << 5) + hash) + ord(x)
    return hash & 0xFFFFFFFF


DATABASE_URL = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}/{DATABASE_NAME}"

engine = create_engine(DATABASE_URL)
if not database_exists(engine.url):
    create_database(engine.url, template="template0")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()



class User(Base):
    __tablename__ = "utilisateurs"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String)
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
    
class UserConnect (BaseModel):
    email : str
    password : str

class UserJWT (BaseModel):
    jwt : str

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

class UserChange (BaseModel):
    email : str
    password : str
    new_password : str
    repeat_new_password : str

class UserPfp(BaseModel):
    img : str




app = FastAPI()

# Endpoint : /
# Type : GET
# this endpoint return à json string containing "Welcome to ProtoRH API !"
@app.get("/")
async def welcolme():
    return {"Welcome to ProtoRH API !"}


# Endpoint : /hello
# Type : GET
# this endpoint return à json string containing "Hello World !"
@app.get("/hello")
async def hello():
    return {"Hello World !"}



# Endpoint : /user/create
# Type : POST
# this endpoint add a user to the table User
@app.post("/user/create", response_model=str)
async def createuser(user : UserCreate):
    query = text("SELECT email FROM utilisateurs WHERE email = :email")
    values = {
        "email": user.email
    }
    with engine.begin() as conn:                                                         #check if the email is already used
            result = conn.execute(query, values).fetchone()
            if result != None:
                raise HTTPException(status_code=403, detail="Email is already used.")


    query = text("INSERT INTO utilisateurs VALUES (DEFAULT, :email, :password, :firstname, :lastname, :birthday_date, :address, :postal_code, :age, '{}', CURRENT_DATE::date, :token, 'user') RETURNING *")

    password_salt = user.password + salt
    password = hashlib.md5(password_salt.encode('utf-8')).hexdigest()    #hashing the password

    repeatpassword_salt = user.repeat_password + salt
    repeat_password = hashlib.md5(repeatpassword_salt.encode('utf-8')).hexdigest()   #hashing the repeat password

    token_raw = user.email + user.firstname + user.lastname + salt
    token = hex(hash_djb2(token_raw))                                   #creating the token

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

    if values["password"] != values["repeat_password"]:                       #password and repeat_password are not the same
        raise HTTPException(status_code=401, detail="Error Password")
    else:
        with engine.begin() as conn:
            result = conn.execute(query, values)
            
            return "User created !"



# Endpoint : /connect
# Type : POST
# this endpoint return a JWT token if the correct email and password are given.
@app.post("/connect", response_model=None)
async def user_connect(user : UserConnect):

    query = text("SELECT email, password, role, id, token FROM utilisateurs WHERE email = :email")

    password_salt = user.password + salt
    password = hashlib.md5(password_salt.encode('utf-8')).hexdigest()         #hashing the password

    values = {
        "email": user.email
    }

    with engine.begin() as conn:
            result = conn.execute(query, values).fetchone()
            if result == None:
                raise HTTPException(status_code=401, detail="Error Email")      #email not correct    
            if result[1] != password:                                           
                raise HTTPException(status_code=401, detail="Error Password")        #password not correct 
            else:
                encoded_jwt = jwt.encode({"token": result[4], "role":result[2]}, SECRET_KEY, algorithm="HS256")
                global user_jwt
                user_jwt = encoded_jwt
                return encoded_jwt



# Endpoint : /user/{user_id}
# Type : GET
# this endpoint return informations on the user. The endpoint is accessible only if a correct JWT is given.
@app.get("/user/{user_id}", response_model = str)
async def user_getdata(user_id : int):
    global user_jwt
    if user_jwt == None:
        raise HTTPException(status_code=401, detail="Please connect first")       #if no jwt = not connected = need to connect
    else:
        decoded_jwt = jwt.decode(user_jwt, SECRET_KEY, algorithms=["HS256"])
        user_role = decoded_jwt["role"]                                          #decode the jwt to have the role of the connected person

        query = text("SELECT id FROM utilisateurs WHERE id = :user_id")

        values = {
            "user_id" : user_id
        }
        with engine.begin() as conn:
            check_id = conn.execute(query, values).fetchone()
            if check_id == None:
                raise HTTPException(status_code=404, detail="Id User not found")

        if user_role == "user":
            query = text("SELECT email, firstname, lastname, age, registrationdate, role FROM utilisateurs WHERE id = :user_id")
        elif user_role == "admin":
            query = text("SELECT email, firstname, lastname, birthdaydate, address, postalcode, age, meta, registrationdate, token, role FROM utilisateurs WHERE id = :user_id")

        
        with engine.begin() as conn:
            result = conn.execute(query, values).fetchone()
            return result

                
# Endpoint : /user/update
# Type : POST
# this endpoint modify informations of the user selected.
@app.post("/user/update", response_model = str)
async def update_user(user : UserModify):
    global user_jwt
    if user_jwt == None:                                                           #if no jwt = not connected = need to connect
        raise HTTPException(status_code=401, detail="Please connect first")
    
    decoded_jwt = jwt.decode(user_jwt, SECRET_KEY, algorithms=["HS256"])
    user_role = decoded_jwt["role"]                                             #decode jwt to have the role and token 
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
            result_jwt = conn.execute(query, values).fetchone()                                                      #recreating the jwt with modified values
            encoded_jwt = jwt.encode({"email": result_jwt[0], "role":result_jwt[2]}, SECRET_KEY, algorithm="HS256")

            user_jwt = encoded_jwt
            return "User modify !"



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

