from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://admin:1234@cluster0.ogyx0.mongodb.net/LMS?retryWrites=true&w=majority&appName=Cluster0")

client = AsyncIOMotorClient(MONGO_URI)
database = client["LMS"]

def get_db():
    return database
