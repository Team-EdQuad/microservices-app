from datetime import datetime, timedelta
from typing import Dict
from fastapi import HTTPException
import logging

from app.utils.mongodb_connection import attendance_store
from app.services.ml_service.prediction_service  import predict_attendance

logger = logging.getLogger(__name__)

async def get_attendance_summary(
    class_id: str,
    subject_id: str,
    start_date: str,
    end_date: str,
    today_date: str  # e.g. "2025-01-23"
) -> Dict:
    try:
        logger.info(f"Request received: class_id={class_id}, subject_id={subject_id}, start_date={start_date}, end_date={end_date}, today_date={today_date}")

        # Parse dates
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        today = datetime.strptime(today_date, "%Y-%m-%d")

        logger.debug(f"Parsed dates - start: {start}, end: {end}, today: {today}")

        # Validate date range
        # if start > end or today < start:
        #     logger.error("Invalid date range: start > end or today < start")
        #     raise ValueError("Invalid date range.")

        # Adjust end_date if today is between start and end
        adjusted_end = min(today, end)

        # 1️⃣ Historical Attendance (including today)
        historical_pipeline = [
            {
                "$match": {
                    "class_id": class_id,
                    "subject_id": subject_id,
                    "date": {"$gte": start_date, "$lte": adjusted_end.strftime("%Y-%m-%d")}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "date": 1,
                    "attendance_percentage": 1
                }
            }
        ]


        logger.debug(f"Aggregation pipeline: {historical_pipeline}")

        history_cursor = attendance_store.aggregate(historical_pipeline)
        history_records = await history_cursor.to_list(length=None)

        logger.info(f"MongoDB returned {len(history_records)} attendance records")

        for rec in history_records:
            logger.debug(f"Record: date={rec.get('date')}, attendance_percentage={rec.get('attendance_percentage')}")

        exist_data = {
            record["date"]: round(record["attendance_percentage"], 2)
            for record in history_records
        }


        logger.info(f"exist_data prepared with {len(exist_data)} entries")

        # 2️⃣ Determine dates to predict
        predict_dates = []

        # Check if today's attendance is marked
        if today.strftime("%Y-%m-%d") not in exist_data:
            predict_dates.append(today.strftime("%Y-%m-%d"))

        # Predict for future dates
        next_day = today + timedelta(days=1)
        while next_day <= end:
            predict_dates.append(next_day.strftime("%Y-%m-%d"))
            next_day += timedelta(days=1)

        predicted_data = {}
        if predict_dates:
            for date in predict_dates:
                result = await predict_attendance(
                    class_id=class_id,
                    subject_id=subject_id,
                    target_date=datetime.strptime(date, "%Y-%m-%d")
                )
                predicted_data[date] = result["predicted_attendance_rate"]

        exist_avg, avg = calculate_averages(exist_data, predicted_data)

        # 4️⃣ Combine Results
        result = {
            "data": {
                "class_id": class_id,
                "subject_id": subject_id,
                "start_date": start_date,
                "end_date": end_date,
                "avg": avg,
                "exist_avg": exist_avg,
                "exist": exist_data,
                "predict": predicted_data
            }
        }

        logger.info("Attendance summary generated successfully.")
        return result

    except Exception as e:
        logger.exception(f"Failed to generate attendance summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    
def calculate_averages(exist_data: dict, predicted_data: dict):
    """
    Calculate exist_avg and avg (excluding -1) from historical and predicted attendance data.

    :param exist_data: Dict[str, float] - historical attendance data
    :param predicted_data: Dict[str, float] - predicted attendance data
    :return: Tuple (exist_avg, avg)
    """
    if exist_data:
        exist_avg = round(sum(exist_data.values()) / len(exist_data), 2)
    else:
        exist_avg = None

    all_values = list(exist_data.values()) + [
        v for v in predicted_data.values() if isinstance(v, (int, float)) and v != -1
    ]
    if all_values:
        avg = round(sum(all_values) / len(all_values), 2)
    else:
        avg = None

    return exist_avg, avg
