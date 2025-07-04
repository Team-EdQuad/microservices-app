from pydantic import BaseModel, Field, EmailStr
from typing import List
from datetime import date

class StudentRegistration(BaseModel):
    student_id: str = Field(..., pattern=r"^STU\d{3}$")
    first_name: str
    last_name: str
    full_name: str
    email: EmailStr
    password: str
    gender: str = Field(..., pattern="^(male|female)$")
    # class_name: str = Field(..., min_length=1, max_length=1, pattern=r"^[A-Z]$")
    # grade: int = Field(..., ge=1, le=13)
    class_id: str
    phone: str = Field(..., pattern=r"^\d{10}$")
    subject: List[str]
    join_date: date
    last_edit_date: date
    club_id: List[str] = []
    sport_id: List[str] = []
    role: str = "student"
