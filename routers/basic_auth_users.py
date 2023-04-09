
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

app = FastAPI()

oauth2 = OAuth2PasswordBearer("login")

class User(BaseModel):
    username: str
    full_name: str
    email: str
    disable: bool

class UserDB(User):
    password: str

users_db = {
    "mouredev": {
        "username": "mouredev",
        "full_name": "Brais Moure",
        "email": "braismoure@mouredev.com",
        "disable": False,
        "password": "123456"
    },
    "manu_dev": {
        "username": "manudev",
        "full_name": "Manuel del Castillo",
        "email": "manuel_dc@icloud.com",
        "disable": True,
        "password": "654321"
    }
}

def search_user(username: str):
    if username in users_db:
        return UserDB(users_db[username])
   
async def current_user(token: str = Depends(oauth2)):
    user = search_user(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="creedencials invalidas",
            headers= {"WW-Authenticate": "bearer"}
        )
    return user

@app.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user_db = users_db.get(form.username)
    if not user_db:
        raise HTTPException(
            status_code=400, detail="El usuario no existe"
        )
    
    user = search_user(form.username)
    if not form.password == user.password:
        raise HTTPException(
            status_code=400, detail="La contraseña es incorrecta"
        )
    
    return {
        "access_token": user.username, "token_type": "bearer"
    }

@app.get("/users/me")
async def me(user: User = Depends(current_user)):
    return user
