from fastapi import HTTPException
from bson.objectid import ObjectId
from app.utils.mongodb_connection import attendance_store

# global dict to cache deleted record metadata (for trigger logic)
attendance_delete_cache = {}


async def delete_class_attendance_service(attendance_id: str):
    try:
        try:
            attendance_object_id = ObjectId(attendance_id)
        except:
            raise HTTPException(status_code=400, detail="Invalid attendance ID format")

        # Fetch record first
        existing_record = await attendance_store.find_one({"_id": attendance_object_id})
        if not existing_record:
            raise HTTPException(status_code=404, detail="Attendance record not found")

        # Save class_id & subject_id in cache (so trigger can use it)
        attendance_delete_cache[str(attendance_object_id)] = {
            "class_id": existing_record["class_id"],
            "subject_id": existing_record["subject_id"],
            "date": existing_record["date"],
            "status": existing_record["status"]
        }

        # Delete the record
        delete_result = await attendance_store.delete_one({"_id": attendance_object_id})
        if delete_result.deleted_count == 0:
            raise HTTPException(status_code=500, detail="Failed to delete attendance record")

        return {"status_code": 200, "message": "Attendance record deleted"}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")