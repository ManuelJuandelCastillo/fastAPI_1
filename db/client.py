from pymongo import MongoClient

# conexion a la DDBB local
#db_client = MongoClient().local

#conexion a la DDBB remota
db_client = MongoClient("mongodb+srv://zurdodel83:mq5i5979FWbkfep8@fastapi-1ddbb.nfgdfz9.mongodb.net/?retryWrites=true&w=majority").test
