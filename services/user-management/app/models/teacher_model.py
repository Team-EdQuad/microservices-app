from pydantic import BaseModel, EmailStr, Field
from datetime import date
from typing import List, Optional, Union

class SubjectClass(BaseModel):
    subject_id: str
    class_id: List[str]


class TeacherModel(BaseModel):
    teacher_id: str
    email: str
    full_name: Optional[str] = None
    first_name: str
    last_name: str
    gender: Optional[str]
    phone_no: Optional[str]  # Note: must match the key you pass
    join_date: str
    last_edit_date: str
    subjects_classes: List[SubjectClass]
    role: str

# class TeacherCreate(BaseModel):
#     first_name: str
#     last_name: str
#     email: EmailStr
#     phone: str
#     subject: List[str]

#     class Config:
#         arbitrary_types_allowed = True


class TeacherCreate(BaseModel):
    teacher_id: str =  Field(..., pattern=r"^TCH\d{3}$")
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    full_name: str
    gender: str
    Phone_no: str
    join_date: date
    last_edit_date: date
    subjects_classes: List[SubjectClass]
    role: str = "teacher"

    class Config:
        arbitrary_types_allowed = True