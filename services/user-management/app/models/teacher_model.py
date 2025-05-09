from pydantic import BaseModel, EmailStr
from typing import List

class TeacherModel(BaseModel):
    teacher_id: str
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    password: str  # Raw password, will be hashed during creation
    subject: List[str]
    role: str = "teacher"

class TeacherCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    subject: List[str]

    class Config:
        arbitrary_types_allowed = True
