# app/routers/prediction_router.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.services.ml_service import prediction_service

router = APIRouter()

class PredictionRequest(BaseModel):
    class_id: str
    subject_id: str
    date: Optional[str] = None

@router.post("/predict-attendance/", tags=["Predictions"])
async def predict_attendance(request: PredictionRequest):
    try:
        # Use provided date or default to today
        target_date = datetime.strptime(
            request.date, "%Y-%m-%d"
        ) if request.date else datetime.now()

        # Call the prediction service
        prediction_result = await prediction_service.predict_attendance(
            request.class_id,
            request.subject_id,
            target_date
        )

        return prediction_result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
