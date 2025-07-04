from fastapi import APIRouter, Depends, HTTPException
from app.models.teacher_model import TeacherCreate
from app.services.auth_service import get_current_user
from app.db.database import db  # Assuming MongoDB is used
from app.models.admin_model import AdminModel
from datetime import datetime

router = APIRouter()

# @router.post("/add-teacher")
# async def add_teacher(teacher: TeacherCreate, current_user: AdminModel = Depends(get_current_user)):
#     """Add a new teacher. Only admins can add teachers."""
#     if current_user.role != "admin":
#         raise HTTPException(status_code=403, detail="Only admins can add new teachers")
#     today = datetime.today()
#     # Insert the new teacher into the database
#     new_teacher = {
#         "teacher_id": teacher.teacher_id,
#         "email": teacher.email,
#         "password": teacher.password,
#         "full_name": teacher.full_name,
#         "first_name": teacher.first_name,
#         "last_name": teacher.last_name,
#         "role": "teacher",  # Assuming role is always teacher for this endpoint
#         "gender": teacher.gender,
#         "Phone_no": teacher.Phone_no,
#         "join_date": datetime(today.year, today.month, today.day),  # Convert to datetime
#         "last_edit_date": datetime(today.year, today.month, today.day),  # Convert to datetime
#         "subjects_classes": [sc.dict() for sc in teacher.subjects_classes]
#     }
#     new_teacher["join_date"] = today.strftime("%Y-%m-%d")
#     new_teacher["last_edit_date"] = today.strftime("%Y-%m-%d")

#     await db["teacher"].insert_one(new_teacher)  # Ensure this operation inserts the data into MongoDB
#     return {"message": "Teacher added successfully"}

@router.post("/add-teacher")
async def add_teacher(teacher: TeacherCreate, current_user: AdminModel = Depends(get_current_user)):
    """Add a new teacher. Only admins can add teachers."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can add new teachers")
    today = datetime.today()
    # Convert Pydantic model to dict
    data = teacher.dict()
    # Set full_name automatically
    data["full_name"] = f"{data['first_name']} {data['last_name']}"
    # Set join_date and last_edit_date to today
    data["join_date"] = today.strftime("%Y-%m-%d")
    data["last_edit_date"] = today.strftime("%Y-%m-%d")
    # Insert into DB
    await db["teacher"].insert_one(data)
    return {"message": "Teacher added successfully"}
