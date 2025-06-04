import re
from fastapi import HTTPException
from app.db.database import db

def validate_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email) is not None

def validate_phone_number(phone: str) -> bool:
    return bool(re.match(r"^0\d{9}$", phone)) 

async def verify_admin_token(token: str) -> bool:
    token = token.replace("Bearer ", "")
    admin_collection = db["admin"]
    admin = await admin_collection.find_one({"token": token})
    return bool(admin)

