from pymongo import MongoClient

# MongoDB URI
client = MongoClient("mongodb+srv://admin:1234@cluster0.ogyx0.mongodb.net/LMS?retryWrites=true&w=majority&appName=Cluster0")

db = client["LMS"]  # Database name