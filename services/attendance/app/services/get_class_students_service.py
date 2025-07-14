from datetime import datetime
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorCollection
from app.utils.mongodb_connection import attendance_store, student, student_attendance_summery


async def get_att_ratio(student_id: str, class_id: str, year: int, subject_id: str) -> float:
    try:
        summary = await student_attendance_summery.find_one({
            "student_id": student_id,
            "class_id": class_id,
            "year": year
        })

        if not summary:
            return 0.0

        for record in summary.get("attendance", []):
            if record.get("subject_id") == subject_id:
                return record.get("current_year", {}).get("yearly_attendance_ratio", 0.0)

        return 0.0

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching attendance ratio: {str(e)}")


async def get_class_students_service(class_id: str, subject_type: str, subject_id: str, date: str):
    try:
        attendance_exists = await attendance_store.find_one(
            {"class_id": class_id, "date": date, "subject_id": subject_id}
        )

        if attendance_exists:
            cursor = attendance_store.find(
                {"class_id": class_id, "date": date, "subject_id": subject_id}
            )
            attendance_data = await cursor.to_list(length=None)

            student_ids = set()
            for record in attendance_data:
                student_ids.update(record.get("status", {}).keys())

            students_cursor = student.find(
                {"student_id": {"$in": list(student_ids)}},
                {"student_id": 1, "full_name": 1}
            )
            student_data = await students_cursor.to_list(length=None)
            student_name_map = {stu["student_id"]: stu["full_name"] for stu in student_data}

            enriched_status_list = []
            for record in attendance_data:
                for sid, stat in record.get("status", {}).items():
                    enriched_status_list.append({
                        "student_id": sid,
                        "full_name": student_name_map.get(sid, "Unknown"),
                        "attendance": stat
                    })

            data = enriched_status_list

        else:
            student_query = {"class_id": class_id}
            if subject_type == "sport":
                student_query["sport_id"] = {"$in": [subject_id]}
            elif subject_type == "club":
                student_query["club_id"] = {"$in": [subject_id]}

            cursor = student.find(
                student_query,
                {"student_id": 1, "full_name": 1}
            )
            data = await cursor.to_list(length=None)

        # Add attendance ratio and convert _id to str
        year = datetime.strptime(date, "%Y-%m-%d").year
        for doc in data:
            doc["_id"] = str(doc["_id"]) if "_id" in doc else None
            student_id = doc.get("student_id")
            if student_id:
                att_ratio = await get_att_ratio(student_id, class_id, year, subject_id)
                doc["att_ratio"] = round(att_ratio, 2)

        return {
            "_id": str(attendance_data[0]["_id"]) if attendance_exists else None,
            "data": data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


