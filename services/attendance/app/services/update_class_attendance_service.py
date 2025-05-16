from datetime import datetime
from bson.objectid import ObjectId
from fastapi import HTTPException
from app.utils.mongodb_connection import attendance_store

async def update_class_attendance_service(
    attendance_id: str,
    class_id: str,
    subject_id: str,
    date: str,
    status: dict
):
    try:
        try:
            attendance_object_id = ObjectId(attendance_id)
        except:
            raise HTTPException(status_code=400, detail="Invalid attendance ID format")

        existing_record = await attendance_store.find_one({"_id": attendance_object_id})
        if not existing_record:
            raise HTTPException(status_code=404, detail="Attendance record not found")

        weekday = datetime.strptime(date, "%Y-%m-%d").strftime("%A")

        updated_data = {
            "class_id": class_id,
            "subject_id": subject_id,
            "date": date,
            "status": status,
            "weekday": weekday,
            "updated_at": int(datetime.now().timestamp())
        }

        update_result = await attendance_store.update_one(
            {"_id": attendance_object_id},
            {"$set": updated_data}
        )

        if update_result.modified_count == 0:
            raise HTTPException(status_code=500, detail="Update failed")

        return {"status_code": 200, "message": "Attendance record updated successfully"}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {str(e)}"
        )
