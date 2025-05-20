from pydantic import BaseModel, Field
from typing import Dict, Literal
from datetime import datetime

class StudentsOfClassRequest(BaseModel):
    """
    Request schema for fetching students of a given class, subject, and date.
    """
    class_id: str
    subject_type: str = "academic"
    subject_id: str = "academic"
    date: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))

class AttendanceEntry(BaseModel):
    """
    Schema for storing or submitting class attendance data.
    """
    class_id: str
    subject_id: str = "academic"
    date: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    status: Dict[str, Literal["present", "absent"]]

class DocumentUpload(BaseModel):
    """
    Schema for storing or submitting class attendance data.
    """
    student_id: str
    class_id: str
    subject_id: str = "academic"
    date: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    file_path: str         # This will be the S3 URL
    file_name: str 
    file_type: Literal["pdf", "docx", "pptx", "xlsx"]
    is_checked: bool = False 
