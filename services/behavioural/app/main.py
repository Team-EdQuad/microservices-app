from fastapi import FastAPI, APIRouter, HTTPException
from .services.database import db
from .models.Behavioral import SubjectResponse 
from typing import List




# Initialize FastAPI app and router
app = FastAPI(title="Behaviral analysis API")
router = APIRouter()


@app.get("/")
async def homepage():
    return {"message": "Welcome to the Behaviral analysis API"}


@router.get("/students/{student_id}/subjects", response_model=List[SubjectResponse])
async def get_subject_names(student_id: str):
    # Fetch student document from 'students' collection
    student = db["student"].find_one({"student_id": student_id})
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    subject_ids = student.get("subject_id", [])
    
    if not subject_ids:
        raise HTTPException(status_code=404, detail="No subject IDs associated with this student")
    
    # Fixed field name to match actual database (lowercase)
    subjects_cursor = db["subject"].find(
        {"subject_id": {"$in": subject_ids}},
        {"_id": 0, "subject_id": 1, "subject_name": 1}  # Fixed field names
    )
    
    subjects_list = list(subjects_cursor)
    
    if not subjects_list:
        raise HTTPException(status_code=404, detail="Subjects not found")
    
    # Map database fields to Pydantic model fields
    subjects = []
    for subject in subjects_list:
        # Convert from database field names to Pydantic model field names
        subjects.append(SubjectResponse(
            Subject_id=subject["subject_id"],
            SubjectName=subject["subject_name"]
        ))
    
    return subjects




# Include the router
app.include_router(router)









