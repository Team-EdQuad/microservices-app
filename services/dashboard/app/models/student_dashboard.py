from pydantic import BaseModel

class SubjectProgress(BaseModel):
    subject_id: str
    class_id: str
    subject_name: str
    total_content: str
    completed_content: str
    progress_percentage: str


class SubjectAssignment(BaseModel):
    assignment_name: str
    subject_name: str
    class_id: str
    deadline: str
    status: str

class AcademicAttendanceRate(BaseModel):
    total_days: str
    days_present: str   
    attendance_rate: str

class ExamMarksResponse(BaseModel):
    subject_name: str
    term: int
    marks: int

