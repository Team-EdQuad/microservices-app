from fastapi import APIRouter, Depends, HTTPException
from app.models.admin_model import AdminCreate
from app.services.auth_service import get_current_user
from app.db.database import db  # Assuming MongoDB is used
from app.models.admin_model import AdminModel

router = APIRouter()

@router.post("/add-teacher")
async def add_teacher(teacher: AdminCreate, current_user: AdminModel = Depends(get_current_user)):
    """Add a new teacher. Only admins can add teachers."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can add new teachers")
    
    # Insert the new teacher into the database
    new_teacher = teacher.dict()
    await db["teachers"].insert_one(new_teacher)  # Ensure this operation inserts the data into MongoDB
    return {"message": "Teacher added successfully", "data": new_teacher}
