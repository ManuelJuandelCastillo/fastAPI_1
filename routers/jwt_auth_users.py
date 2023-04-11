from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta

ALGORITHM = "HS256"
ACCESS_TOKEN_DURATION = 1
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
# para generar la llave
# openssl rand -hex 32
# en bash


router = APIRouter()

crypt = CryptContext(schemes="bcrypt")

oauth2 = OAuth2PasswordBearer("login")


class User(BaseModel):
    username: str
    full_name: str
    email: str
    disabled: bool


class UserDB(User):
    password: str


users_db = {
    "mouredev": {
        "username": "mouredev",
        "full_name": "Brais Moure",
        "email": "braismoure@mouredev.com",
        "disabled": False,
        "password": "$2y$10$1pZcREOlMqG8PNlOQxduluvsYTimHjZ3wM22UbV8fPAmlUiKfi.GK"
    },
    "manu_dev": {
        "username": "manudev",
        "full_name": "Manuel del Castillo",
        "email": "manuel_dc@manu.com",
        "disabled": True,
        "password": "$2y$10$jtBD94hK11CyCHnFgoHrkuKRJE44hj3our9Nvu881ql2i3qFlF9wu"
    }
}


async def auth_user(token: str = Depends(oauth2)):
    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales invalidas",
        headers={"WW-Authenticate": "Bearer"}
    )

    # obtener los datos de usuario contemidos en el token
    try:
        username = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM).get("sub")
        if username is None:
            raise exception
        
    except JWTError:
        raise exception
    
    return search_user(username)


async def current_user(user: User = Depends(auth_user)):
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
    return user

def search_user(username: str):
    if username in users_db:
        return User(**users_db[username])

def search_user_db(username: str):
    if username in users_db:
        return UserDB(**users_db[username])


@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user_db = users_db.get(form.username)
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario inexistente"
        )

    user = search_user_db(form.username)

    if not crypt.verify(form.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="La contraseña es incorrcta"
        )

    # momento en el que expira el token
    # momento en el que se genera (utcnow)
    # mas el tiempo que tarda en expirar (access token duration) definido al principio
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_DURATION)

    access_token = {"sub": user.username, "exp": expire}

    return {"access_token": jwt.encode(access_token, SECRET_KEY, algorithm=ALGORITHM), "token_type": "bearer"}


@router.get("/users/me")
async def me(user: User = Depends(current_user)):
    return user
