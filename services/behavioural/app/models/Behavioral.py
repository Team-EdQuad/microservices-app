
from typing import Optional
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



class UpdateResponse(BaseModel):
    success: bool
    message: str
    subject_id: str
    class_id: str
    updated_week: int
    calculated_data: dict


class PredictionOutput(BaseModel):
    predicted_active_time: float

class TrainingResponse(BaseModel):
    success: bool
    message: str
    training_score: Optional[float] = None
    trained_at: Optional[str] = None

class ModelStatus(BaseModel):
    model_exists: bool
    model_info: Optional[dict] = None



class PredictionInput(BaseModel):
    # Only include fields the frontend can send
    SpecialEventThisWeek: int
    ResourcesUploadedThisWeek: int

    class Config:
        json_schema_extra = {
            "example": {
                "SpecialEventThisWeek": 1,
                "ResourcesUploadedThisWeek": 5
            }
        }
