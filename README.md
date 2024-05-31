# ProtoRH API

## How to start the API 

First you need to setup all the needs for the api with this command : 

```sh build.sh```


To run the api you need to execute this command : 

```sh run.sh```


## /hello
**Data required**:

 None

**Type of return** : 

JSON 

**Exemple of curl** :

 ```curl -X GET http://localhost:4242/hello```

**Description** :

 This endpoint only return "Hello World !"

## /user/create

**Data required** :

```
{
  "email": "string",
  "password": "string",
  "repeat_password": "string",
  "firstname": "string",
  "lastname": "string",
  "birthday_date": "string",
  "address": "string",
  "postal_code": "string"
}
 ```

**Type of return** : 

Error 403, Error 401, "User Created !"

**Exemple of curl** :

```curl --header "Content-Type: application/json" --request POST --data '{     "email": "jean.bon@gmail.com",     "password" : "motdepasse", "repeat_password" : "motdepasse",    "firstname" : "Jean",     "lastname" : "Bon",     "birthday_date" : "1998-12-12",     "address" : "36 rue des Jambons",     "postal_code" : "42424"      }' http://localhost:4242/user/create```

**Description** : 

This endpoint allows for the creation of a user and insertion into the 'users' table. You can choose the email, password, and other information, while certain data such as ID, age, metadata, token, registration date, and role are generated automatically. The password is hashed before being stored to comply with RGPD standards.

## /connect

**Data required** :

```
{
  "email": "string",
  "password": "string"
}
 ```

**Type of return** : 

Error 401

**Exemple of curl** :

```curl --header "Content-Type: application/json" --request POST --data '{     "email": "jean.bon@gmail.com",     "password" : "motdepasse"    }' http://localhost:4242/user/create```

**Description** : 

This endpoint allows existing users to connect by entering their email as well as their password which will be hashed and then compared with the password contained in the database

## /user/{id_user}

**Data required** : 

No data required, bu the user must be connected

**Type of return** : 

Error 401

**Exemple of curl** :

 ```curl -X GET http://localhost:4242/user/1```

**Description** : 

This endpoint allows users who have the user role to retrieve email, first name, last name. Users with the admin role can recover everything except the password.

## /user/update

**Data required** : 

role = user :

```
{
  "email": "string",
  "birthday_date": "string",
  "address": "string",
  "postal_code": "string",
  "age": "string",
  "meta": "string",
  "registration_date": "string",
}
```

role = admin : 

```
{
  "id": "string",
  "email": "string",
  "firstname": "string",
  "lastname": "string",
  "birthday_date": "string",
  "address": "string",
  "postal_code": "string",
  "age": "string",
  "meta": "string",
  "registration_date": "string",
  "role": "string"
}
```

**Type of return** : 

Error 401, "User modify !"

**Exemple of curl** :

```curl --header "Content-Type: application/json" --request POST --data '{ "email": "jean.bon@gmail.com",     "password" : "motdepasse",     "firstname" : "Jean",     "lastname" : "Bon",     "birthday_date" : "1998-12-12",     "address" : "36 rue des jambons jours",     "postal_code" : "42424","age" : "42", "meta": "{}","registration_date":"2023-10-31", "role":"admin"      }' http://localhost:4242/user/update```

**Description** : 

This endpoint allows users who have the user role to modify their own information. Users with the admin role can choose the user for whom they want to change the information.

## /user/password

**Data required** : 

```
{
  "email": "string",
  "password": "string",
  "new_password": "string",
  "repeat_new_password": "string"
}
```

**Type of return** : 

Error 401, "The password has been modified !"

**Exemple of curl** :

```curl --header "Content-Type: application/json" --request POST --data '{"email":"jean.bon@gmail.com", "password":"motdepasse", "new_password":"newmotdepasse", "repeat_new_password":"newmotdepasse"}' http://localhost:4242/user/password```

**Description** : 

This endpoint allows users to change their password by entering their old password and then entering their new password twice.

## /user/password

**Data required** : 

```
{
  "img": "string"
}
```

**Type of return** : 

"User not found"

**Exemple of curl** :

```curl --header "Content-Type: application/json" --request POST --data '{"email":"jean.bon@gmail.com", "password":"motdepasse", "new_password":"newmotdepasse", "repeat_new_password":"newmotdepasse"}' http://localhost:4242/user/password```

**Description** : 

This endpoint allows users to upload an image as their profile photo. If the image given is not find, the standard profile picture is return.

## /picture/user/{user_id}

**Data required** : None

**Type of return** : 

"User not found", Profile Picture, Standard Profile Picture

**Exemple of curl** :

 ```curl -X GET http://localhost:4242/picture/user/1```

**Description** : 

This endpoint allows you to retrieve a user's profile image. If the user doesn't have a personalized profile picture the standard profile picture is given.



### Copyright © 2023 Nicolas ARCHAMBAULT--BONNET Jordan AUTIE