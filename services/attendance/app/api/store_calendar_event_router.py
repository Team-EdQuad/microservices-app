from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from ..services.store_calendar_event_service import store_calendar_event
from pydantic import BaseModel
from typing import Dict

router = APIRouter(
    tags=["Calender"],
    prefix="/attendance"
)


class CalendarEventFeatures(BaseModel):
    is_exam_week: int
    is_event_day: int
    is_school_day: int

class CalendarEventRequest(BaseModel):
    class_id: str
    subject_id: str
    date: str  # Could also use datetime.date if you want auto-validation
    features: CalendarEventFeatures


@router.post("/store-calendar-event")
async def create_calendar_event(event_data: CalendarEventRequest):
    try:
        # Convert to dictionary for DB insertion (if needed)
        event_dict = event_data.dict()
        
        result = await store_calendar_event(event_dict)
        
        return {"message": "Calendar event stored successfully", "event_id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))