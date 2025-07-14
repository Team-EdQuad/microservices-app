from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import List
from datetime import date
from app.db.database import db 
from bson import ObjectId

router = APIRouter()

class UpdateStudentRequest(BaseModel):
    student_id: str
    first_name: str
    last_name: str
    gender: str
    email: EmailStr
    password: str
    class_id: str
    phone_no: str
    subject_id: List[str]
    join_date: str
    last_edit_date: str
    club_id: List[str]
    sport_id: List[str]
    role: str

@router.post("/update-student")
async def update_student(student_data: UpdateStudentRequest):
    existing = await db["student"].find_one({"student_id": student_data.student_id})
    if not existing:
        raise HTTPException(404, "Student not found")

    update_data = student_data.dict(exclude_unset=True)

    for field in ["password", "join_date", "role", "_id", "club_id", "sport_id"]:
        update_data.pop(field, None)

    update_data["full_name"] = f"{update_data.get('first_name', existing['first_name'])} {update_data.get('last_name', existing['last_name'])}"
    
    await db["student"].update_one(
        {"student_id": student_data.student_id},
        {"$set": update_data}
    )
    return {"message": "Student updated successfully"}


@router.get("/get-student-data")
async def get_student_data(student_id: str):
    student = await db["student"].find_one({"student_id": student_id})

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Convert ObjectId to string
    student["_id"] = str(student["_id"])

    return student