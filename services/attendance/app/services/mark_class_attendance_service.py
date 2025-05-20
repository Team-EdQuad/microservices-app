from datetime import datetime
from app.utils.mongodb_connection import attendance_store

async def mark_class_attendance_service(class_id: str, subject_id: str, date: str, status: dict):
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        weekday = date_obj.strftime("%A")

        attendance_data = {
            "class_id": class_id,
            "subject_id": subject_id,
            "date": date,
            "weekday": weekday,
            "status": status
        }

        await attendance_store.insert_one(attendance_data)

        return {"message": "Attendance record added successfully", "success": True}

    except Exception as e:
        raise Exception(f"Failed to mark attendance: {str(e)}")
