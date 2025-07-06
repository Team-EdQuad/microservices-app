import calendar
from datetime import datetime, timedelta
from typing import Dict
from fastapi import APIRouter, HTTPException
from app.services.background_services.get_daily_attendance_service import get_attendance_summary
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["Dashboard"],
    prefix="/attendance"
)

@router.get("/daily_summary")
async def get_daily_summary(
    class_id: str,
    subject_id: str,
    month: str,      # e.g. "2" for February or "February"
    week: int,       # e.g. 1, 2, 3
    today_date: str  # e.g. "2025-06-07"
) -> Dict:
    """
    Generate a daily attendance summary for the given week of a specific month.
    """
    try:
        today = datetime.strptime(today_date, "%Y-%m-%d")
        year = today.year

        # Convert the month to an integer
        try:
            if month.isalpha():
                month_num = list(calendar.month_name).index(month.capitalize())
            else:
                month_num = int(month)
            if not (1 <= month_num <= 12):
                raise ValueError
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid month parameter. Use 1-12 or full month name.")

        # Get the first and last day of the selected month
        first_day = datetime(year, month_num, 1)
        last_day_num = calendar.monthrange(year, month_num)[1]
        last_day = datetime(year, month_num, last_day_num)

        # Calculate all Mondays in the selected month
        mondays = []
        current_day = first_day
        while current_day <= last_day:
            if current_day.weekday() == 0:  # Monday
                mondays.append(current_day)
            current_day += timedelta(days=1)

        if week < 1 or week > len(mondays):
            raise HTTPException(status_code=400, detail=f"Invalid week parameter. This month has {len(mondays)} weeks starting on Monday.")

        monday = mondays[week - 1]
        sunday = monday + timedelta(days=6)

        # Clip the range to stay within the month
        start_date = max(monday, first_day)
        end_date = min(sunday, last_day)

        daily_summary = {}

        current_day = start_date
        while current_day <= end_date:
            date_str = current_day.strftime("%Y-%m-%d")
            summary = await get_attendance_summary(
                class_id=class_id,
                subject_id=subject_id,
                start_date=date_str,
                end_date=date_str,
                today_date=today_date
            )

            logger.info(f"Daily summary for {date_str}: {summary}")

            exist_avg = summary.get("exist_avg") or summary.get("data", {}).get("exist_avg")

            if exist_avg is None:
                logger.warning(f"Missing 'exist_avg' for {date_str}. Defaulting to 0.0")
                exist_avg = 0.0

            daily_summary[date_str] = exist_avg

            current_day += timedelta(days=1)

        return {
            "class_id": class_id,
            "subject_id": subject_id,
            "daily_summary": daily_summary
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.exception(f"Failed to generate daily summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate daily summary: {e}")
