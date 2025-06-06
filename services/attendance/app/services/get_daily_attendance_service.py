# import logging
# from datetime import datetime
# from typing import Dict
# from app.utils.mongodb_connection import attendance_store

# logger = logging.getLogger(__name__)

# async def get_daily_attendance(
#     class_id: str,
#     subject_id: str,
#     start_date: str,
#     end_date: str
# ) -> Dict[str, float]:
#     """
#     Get daily attendance percentages for a class and subject within a date range.

#     Args:
#         class_id (str): The class ID
#         subject_id (str): The subject ID
#         start_date (str): Start date in YYYY-MM-DD format
#         end_date (str): End date in YYYY-MM-DD format

#     Returns:
#         Dict[str, float]: Dictionary of daily attendance percentages (date: percentage)
#     """
#     logger.info(f"Fetching daily attendance for class_id={class_id}, "
#                 f"subject_id={subject_id}, start_date={start_date}, end_date={end_date}")
    
#     try:
#         # Validate date formats
#         start = datetime.strptime(start_date, "%Y-%m-%d")
#         end = datetime.strptime(end_date, "%Y-%m-%d")
#         if start > end:
#             logger.warning(f"Invalid date range: start_date={start_date} is after end_date={end_date}")
#             raise ValueError("Start date must be before or equal to end date")
#     except ValueError as e:
#         logger.error(f"Date validation failed: {e}")
#         if "strptime" in str(e):
#             raise ValueError("Invalid date format. Use YYYY-MM-DD")
#         raise e

#     try:
#         # Build aggregation pipeline
#         attendance_pipeline = [
#             {
#                 "$match": {
#                     "class_id": class_id,
#                     "subject_id": subject_id,
#                     "date": {
#                         "$gte": start_date,
#                         "$lte": end_date
#                     }
#                 }
#             },
#             {
#                 "$addFields": {
#                     "statusArray": {
#                         "$objectToArray": "$status"
#                     }
#                 }
#             },
#             {
#                 "$unwind": "$statusArray"
#             },
#             {
#                 "$group": {
#                     "_id": "$date",
#                     "present_students": {
#                         "$sum": {
#                             "$cond": [
#                                 {"$eq": [{"$toLower": "$statusArray.v"}, "present"]},
#                                 1,
#                                 0
#                             ]
#                         }
#                     },
#                     "total_students": {"$sum": 1}
#                 }
#             },
#             {
#                 "$sort": {"_id": 1}
#             }
#         ]

#         logger.debug(f"Running attendance pipeline: {attendance_pipeline}")
#         attendance_cursor = attendance_store.aggregate(attendance_pipeline)
#         attendance_records = await attendance_cursor.to_list(length=None)
#         logger.info(f"Retrieved {len(attendance_records)} attendance record(s)")

#         # Build the result dictionary
#         result = {}
#         for record in attendance_records:
#             date_str = record["_id"]  # date is already a string
#             present = record["present_students"]
#             total = record["total_students"]

#             if total == 0:
#                 percentage = 0.0
#             else:
#                 percentage = (present / total) * 100

#             result[date_str] = round(percentage, 2)

#         logger.info("Attendance calculation completed successfully.")
#         return result

#     except Exception as e:
#         logger.exception(f"Error while fetching attendance data: {e}")
#         raise e






from datetime import datetime, timedelta
from typing import Dict
from fastapi import HTTPException
import logging

from app.utils.mongodb_connection import attendance_store
# from app.ml_model import predict_attendance_for_dates  # hypothetical function

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

        if start > end or today < start:
            logger.error("Invalid date range: start > end or today < start")
            raise ValueError("Invalid date range.")

        # 1️⃣ Historical Attendance (including today)
        historical_pipeline = [
            {
                "$match": {
                    "class_id": class_id,
                    "subject_id": subject_id,
                    "date": {"$gte": start_date, "$lte": end_date}
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

        # # 2️⃣ Determine dates to predict
        # predict_dates = []

        # # Check if today's attendance is marked
        # if today.strftime("%Y-%m-%d") not in exist_data:
        #     predict_dates.append(today.strftime("%Y-%m-%d"))

        # # Predict for future dates
        # next_day = today + timedelta(days=1)
        # while next_day <= end:
        #     predict_dates.append(next_day.strftime("%Y-%m-%d"))
        #     next_day += timedelta(days=1)

        # # 3️⃣ Predict attendance using ML model
        # predicted_data = {}
        # if predict_dates:
        #     predictions = predict_attendance_for_dates(
        #         class_id=class_id,
        #         subject_id=subject_id,
        #         dates=predict_dates
        #     )
        #     predicted_data = {
        #         date: round(percentage, 2)
        #         for date, percentage in predictions.items()
        #     }

        # 4️⃣ Combine Results
        result = {
            "data": {
                "class_id": class_id,
                "subject_id": subject_id,
                "start_date": start_date,
                "end_date": end_date,
                "exist": exist_data,
                # "predict": predicted_data
            }
        }

        logger.info("Attendance summary generated successfully.")
        return result

    except Exception as e:
        logger.exception(f"Failed to generate attendance summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))
