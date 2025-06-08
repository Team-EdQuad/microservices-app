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

@router.get("/weekly_summary")
async def get_weekly_summary(
    class_id: str,
    subject_id: str,
    month: str,       # e.g. "2" for February or "02" or "february"
    today_date: str   # e.g. "2025-06-07"
) -> Dict:
    """
    Generate a weekly attendance summary for the given month (week1, week2, ...) using exist_avg.
    """
    try:
        today = datetime.strptime(today_date, "%Y-%m-%d")
        year = today.year

        # Convert the month to an integer
        try:
            # If month is a name like "February"
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
        current_day = first_day
        weekly_summary = {}
        week_counter = 1

        while current_day <= last_day:
            # Find the Monday of the current week
            monday = current_day - timedelta(days=current_day.weekday())
            # Find the Sunday of the current week
            sunday = monday + timedelta(days=6)

            # Clip the range to stay within the month
            start_date = max(monday, first_day)
            end_date = min(sunday, last_day)

            # Format as strings
            start_date_str = start_date.strftime("%Y-%m-%d")
            end_date_str = end_date.strftime("%Y-%m-%d")

            summary = await get_attendance_summary(
                class_id=class_id,
                subject_id=subject_id,
                start_date=start_date_str,
                end_date=end_date_str,
                today_date=today_date
            )

            logger.info(f"Weekly summary for {month} week{week_counter}: {summary}")

            exist_avg = summary.get("exist_avg") or summary.get("data", {}).get("exist_avg")

            if exist_avg is None:
                logger.warning(f"Missing 'exist_avg' for week {week_counter}. Defaulting to 0.0")
                exist_avg = 0.0

            weekly_summary[f"week{week_counter}"] = exist_avg

            # Move to next week (Monday)
            current_day = monday + timedelta(days=7)
            week_counter += 1

        return {
            "class_id": class_id,
            "subject_id": subject_id,
            "weekly_summary": weekly_summary
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.exception(f"Failed to generate weekly summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate weekly summary: {e}")
