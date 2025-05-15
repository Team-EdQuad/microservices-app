from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

#subject names
class SubjectResponse(BaseModel):
    Subject_id: str  
    SubjectName: str  

class ContentResponse(BaseModel):
    content_id: str
    content_name: str
    content_file_path: Optional[str] = None  # Optional field
    Date: Optional[datetime] = None
    description: Optional[str] = None
    class_id: str
    subject_id: str  

class MarksResponse(BaseModel):
    term: int
    subject_id: str
    subject_name: str  # New field for subject name
    marks: float
    class_id: str
    class_name: str  # New field for class name
    exam_year: int


class SubjectClassResponse(BaseModel):
    subject_id: str
    subject_name: str
    

class ClassResponse(BaseModel):
    class_id: str  
    class_name: str  



class SubjectWithClasses(BaseModel):
    subject_id: str
    subject_name: str
    classes: List[ClassResponse]

class SubjectClassResponse(BaseModel):
    subjects_classes: List[SubjectWithClasses]



#student submission
class SubmissionResponse(BaseModel):
    submission_id: str
    subject_id: str
    content_file_path: str
    submit_time_date: datetime
    class_id: str
    file_name: str
    marks: Optional[int] = None
    assignment_id: str
    student_id: str
    teacher_id: str


class AssignmentItem(BaseModel):
    assignment_id: str
    assignment_name: str
    created_at: datetime 

# List response
class AssignmentListResponse(BaseModel):
    assignments: List[AssignmentItem]



#student assignment view
class AssignmentViewResponse(BaseModel):
    assignment_id: str
    assignment_name: str
    assignment_file_path : str
    Deadline: datetime
    class_id: str
    subject_id: str
    description: Optional[str] = None
   




#teacher assignment creation
class AssignmentResponse(BaseModel):
    assignment_id: str
    assignment_name: str
    description: str
    deadline: datetime
    assignment_file_path: str
    class_id: str
    subject_id: str
    teacher_id: str
    grading_type: str
    sample_answer: Optional[str] = None
    created_at: datetime 


#student  view assignment marks
class AssignmentMarksResponse(BaseModel):
       teacher_id: str
       subject_id: str
       subject_name: Optional[str] = None   
       assignment_id: str
       marks: Optional[int] = None 
       assignment_name: Optional[str] = None
       
#teacher upload content 
class ContentUploadResponse(BaseModel):
    content_id: str
    content_name: str
    content_file_path: str
    upload_date: str
    description: str
    class_id: str
    subject_id: str

class Exam(BaseModel):
    exam_id: str
    term: int  # Term as an integer (e.g., 1, 2, 3)
    marks: float

class SubjectExams(BaseModel):
    subject_id: str
    subject_name: Optional[str] = None  # This will be fetched from DB
    exams: List[Exam]

class ExamMarksResponse(BaseModel):
    student_id: str
    exam_year: int
    class_id: str
    class_name: Optional[str] = None  # This will be fetched from DB
    exam_marks: List[SubjectExams]
    