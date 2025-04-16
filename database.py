

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.collection import Collection

mongo_uri = "mongodb://localhost:27017/"
db_name = "MyDataBase"

client = AsyncIOMotorClient('mongodb://localhost:27017')
db = client[db_name]

register_collection = db["registered_users"]

employee_collection = db["employees"]

order_collection = db["orders"]

items_collection = db["items"]



