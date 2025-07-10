from pydantic import BaseModel,Field, EmailStr
from typing import List
from datetime import date
from datetime import datetime
from typing import Optional, Union


class LoginRequest(BaseModel):
    username: str
    password: str



class AdminModel(BaseModel):
    admin_id: str
    first_name: str
    last_name: str
    full_name: str
    email: str
    phone: str
    password: str  # Raw password, will be hashed during creation
    role: str  # Role can be admin, student, teacher, etc.
    join_date: Optional[Union[date, datetime]] = None
    last_edit: Optional[Union[date, datetime]] = None
    gender: str



class AdminCreate(BaseModel):
    admin_id: str = Field(..., pattern=r"^ADM\d{3}$")
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    phone: str = Field(..., pattern=r"^\d{10}$")
    role: str = "admin"
    full_name: Optional[str] = None
    join_date: Optional[Union[date, datetime]] = None
    last_edit_date: Optional[Union[date, datetime]] = None
    gender: str = Field(..., pattern="^(male|female)$")

    class Config:
        arbitrary_types_allowed = True

class StudentRegistration(BaseModel):
    student_id: str = Field(..., pattern=r"^STU\d{3}$")
    first_name: str
    last_name: str
    full_name: str = None  # optional, can be omitted in request
    email: EmailStr
    password: str
    gender: str = Field(..., pattern="^(male|female)$")
    class_id: str
    phone_no: str = Field(..., pattern=r"^\d{10}$")
    subject_id: Optional[List[str]] = []
    join_date: date
    last_edit_date: date
    club_id: List[str] = []
    sport_id: List[str] = []
    role: str = "student"


class SubjectClass(BaseModel):
    subject_id: str
    class_id: List[str]

class TeacherCreate(BaseModel):
    teacher_id: str =  Field(..., pattern=r"^TCH\d{3}$")
    email: EmailStr
    password: str
    full_name: str
    first_name: str
    last_name: str
    gender: str
    Phone_no: str
    join_date: date
    last_edit_date: date
    subjects_classes: List[SubjectClass]
    role: str = "teacher"

    class Config:
        arbitrary_types_allowed = True

class UserProfileUpdate(BaseModel):
    full_name: str
    gender: str = Field(..., pattern="^(male|female|other)$", description="Must be 'male', 'female', or 'other'")
    language: str
    email: str
    phone: str = Field(..., pattern=r"^0\d{9}$")
    role: str
    joined_date: str


class UpdatePasswordRequest(BaseModel):
    email: str
    password: str

