from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict
from ..services.background_services.get_daily_attendance_service import get_attendance_summary

router = APIRouter(
    tags=["Attendance"],
    prefix="/attendance"
)

class AttendanceSummaryResponse(BaseModel):
    class_id: str
    subject_id: str
    start_date: str
    end_date: str
    avg: float
    exist_avg: float
    exist: Dict[str, float]
    predict: Dict[str, float]

@router.get("/summary", response_model=AttendanceSummaryResponse)
async def get_attendance_summary_endpoint(
    class_id: str,
    subject_id: str,
    start_date: str,
    end_date: str,
    today_date: str
):
    try:
        result = await get_attendance_summary(class_id, subject_id, start_date, end_date, today_date)
        return result["data"]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
