from app.models.teacher_model import TeacherModel
from fastapi import HTTPException
from app.db.database import db

async def add_teacher_to_db(teacher_data: TeacherModel):
    """Add teacher to the database."""
    teacher_doc = teacher_data.dict()
    result = await db["teacher"].insert_one(teacher_doc)
    
    if result.inserted_id:
        teacher_data.teacher_id = str(result.inserted_id)
        return teacher_data
    else:
        raise HTTPException(status_code=500, detail="Failed to add teacher")
