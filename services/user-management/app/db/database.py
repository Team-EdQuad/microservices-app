# app/db/database.py

from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = "mongodb+srv://admin:1234@cluster0.ogyx0.mongodb.net/LMS?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "LMS"


db_client = AsyncIOMotorClient(MONGO_URI)
db = db_client[DB_NAME]

async def connect_to_mongo():
    global client, db
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    print("Connected to MongoDB")

async def close_mongo_connection():
    global client
    if client:
        client.close()
        print("Disconnected from MongoDB")

def get_database():
    return db
