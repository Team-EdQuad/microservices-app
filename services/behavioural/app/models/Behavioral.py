
from pydantic import BaseModel



class StartAccess(BaseModel):
    studentId: str
    contentId: str
    subjectId: str
    classId: str
    accessBeginTime: str  # ISO format

class EndAccess(BaseModel):
    studentId: str
    contentId: str
    closeTime: str  # ISO format
