from fastapi import APIRouter, HTTPException
from app.utils.mongodb_connection import student, sports, clubs


async def get_student_nonacadamic_subjects_service(student_id: str):
    try:
        student_doc = await student.find_one({"student_id": student_id})

        if not student_doc:
            raise HTTPException(status_code=404, detail="Student not found")

        sports_ids = student_doc.get("sport_id", [])
        clubs_ids = student_doc.get("club_id", [])

        subject_ids = sports_ids + clubs_ids

        return {"subject_ids": subject_ids}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving subject IDs: {str(e)}"
        )
    

async def get_all_nonacadamic_subjects_service():
    try:
        sports_cursor = sports.find({}, {"_id": 0, "sport_id": 1})
        clubs_cursor = clubs.find({}, {"_id": 0, "club_id": 1})

        sports_ids = [doc["sport_id"] async for doc in sports_cursor]
        club_ids = [doc["club_id"] async for doc in clubs_cursor]

        subject_ids = sports_ids + club_ids

        return {"subject_ids": subject_ids}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving all subject IDs: {str(e)}"
        )
