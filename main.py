from fastapi import FastAPI
from routers import jwt_auth_users, products, users_db

app = FastAPI()

app.include_router(jwt_auth_users.router)
app.include_router(products.router)
app.include_router(users_db.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}
