# app/services/update_password_service.py

from fastapi import HTTPException
from app.models.update_password_model import UpdatePasswordRequest
from app.db.database import db

# Helper function to determine collection
async def get_collection_by_email(email: str):
    if await db.teacher.count_documents({"email": email}) > 0:
        return db.teacher
    elif await db.student.count_documents({"email": email}) > 0:
        return db.student
    elif await db.admin.count_documents({"email": email}) > 0:
        return db.admin
    return None

# Main logic to update password
async def update_user_password(request: UpdatePasswordRequest):
    collection = await get_collection_by_email(request.email)
    
    if collection is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    result = await collection.update_one(
        {"email": request.email},
        {"$set": {"password": request.password}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="Password update failed")
    
    return {"message": "Password updated successfully"}
