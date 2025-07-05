# microservices-app-dev/services/calendar/app/services/database.py

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection

MONGO_URI = "mongodb+srv://admin:1234@cluster0.ogyx0.mongodb.net/LMS?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "LMS" 

client: MongoClient = MongoClient(MONGO_URI)
db: Database = client[DB_NAME]

def get_collection(collection_name: str) -> Collection:
    """
    Returns a specific MongoDB collection instance from the connected database.
    """
    return db[collection_name]