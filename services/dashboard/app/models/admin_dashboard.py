from pydantic import BaseModel
from typing import List, Optional

class ExamMarksResponse(BaseModel):
    subject_name: str
    term: int
    marks: float


class StudentProgress (BaseModel):
    student_name: str
    first_term_avg: float
    second_term_avg: float
    third_term_avg: float
    academic_attendance_rate: float
    non_academic_attendance_rate: float
    avg_academic_progress: float


class UserLite(BaseModel):
    user_id: str
    full_name: str
    role: str