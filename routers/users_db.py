from fastapi import APIRouter, HTTPException, status
from db.models.user import User
from db.client import db_client
from db.schemas.user import user_schema, users_schema
from bson import ObjectId


router = APIRouter(
    prefix="/userdb",
    tags=["userdb"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "No encontrado"}}
)

def search_user(field: str, key): 
    try:
        user = db_client.local.users.find_one({field: key})
        return User(**user_schema(user))
    except:
        return {"error": "No se ha encontrado el usuario"}

@router.get("/", response_model=list[User])
async def users():
    return users_schema(db_client.local.users.find())

@router.get("/{id}")
async def user(id: str):
    return search_user("_id", ObjectId(id))   
    
@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def user(user: User):
    if type(search_user("email", user.email)) == User:
        raise HTTPException(
           status_code=status.HTTP_400_BAD_REQUEST, detail="el email ya esta registrado"
        )

    user_dict = dict(user)
    # eliminamos es campo id del dict ya que MongoDB asigna un id unico al generar el registro
    del user_dict["id"]
    id = db_client.local.users.insert_one(user_dict).inserted_id
    
    new_user = user_schema(db_client.local.users.find_one({"_id": id}))
    # utilizando el esquema de la funcion schema pasamos el user insertado
    # en la DDBB al formato de usuario que utilizamos en la API

    return User(**new_user)

@router.put("/", response_model=User)
async def user(user: User):
    
    user_dict = dict(user)
    del user_dict["id"]

    try:
        db_client.local.users.find_one_and_replace({"_id": ObjectId(user.id)}, user_dict)
    except:
        return {"error": "No se ha encontrado el usuario"}

    return search_user("_id", ObjectId(user.id))
    
@router.delete("/{id}")
async def user(id: str):
    found = db_client.local.users.find_one_and_delete({"_id": ObjectId(id)})
    
    if not found:
        return {"error": "nose ha encontrado el usuario"}