import calendar
from datetime import datetime
from typing import Dict
from fastapi import APIRouter, HTTPException
from app.services.background_services.get_daily_attendance_service import get_attendance_summary
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["Dashboard"],
    prefix="/attendance"
)

@router.get("/monthly_summary")
async def get_monthly_summary(
    class_id: str,
    subject_id: str,
    today_date: str  # e.g. "2025-06-07"
) -> Dict:
    """
    Generate a monthly attendance summary (per month exist_avg).
    """
    try:
        today = datetime.strptime(today_date, "%Y-%m-%d")
        year = today.year

        monthly_summary = {}

        # Loop through months from January to current month
        for month in range(1, today.month + 1):
            # Compute first and last day of the month
            start_date = datetime(year, month, 1).strftime("%Y-%m-%d")
            last_day = calendar.monthrange(year, month)[1]
            end_date = datetime(year, month, last_day).strftime("%Y-%m-%d")

            try:
                summary = await get_attendance_summary(
                    class_id=class_id,
                    subject_id=subject_id,
                    start_date=start_date,
                    end_date=end_date,
                    today_date=today_date
                )

                logger.info(f"Monthly summary for {calendar.month_name[month]}: {summary}")

                # Use .get() with fallback
                exist_avg = summary.get("exist_avg") or summary.get("data", {}).get("exist_avg")

                if exist_avg is None:
                    logger.warning(f"Missing 'exist_avg' for {calendar.month_name[month]}. Defaulting to 0.0")
                    exist_avg = 0.0

                month_name = calendar.month_name[month].lower()
                monthly_summary[month_name] = exist_avg

            except Exception as e:
                logger.error(f"Error processing month {calendar.month_name[month]}: {e}")
                month_name = calendar.month_name[month].lower()
                monthly_summary[month_name] = 0.0  # Default to 0.0 if error

        return {
            "class_id": class_id,
            "subject_id": subject_id,
            "monthly_summary": monthly_summary
        }

    except Exception as e:
        logger.exception(f"Failed to generate monthly summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate monthly summary: {e}")
