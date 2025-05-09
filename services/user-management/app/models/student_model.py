from pydantic import BaseModel, Field, EmailStr
from typing import List

class StudentRegistration(BaseModel):
    student_id: str = Field(..., pattern=r"^STU\d{4}$")
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    gender: str = Field(..., pattern="^(male|female)$")
    class_name: str = Field(..., min_length=1, max_length=1, pattern=r"^[A-Z]$")
    grade: int = Field(..., ge=1, le=13)
    phone: str = Field(..., pattern=r"^0\d{9}$")
    subject: List[str]
    language: str
    club_id: List[str] = []
    sport_id: List[str] = []
