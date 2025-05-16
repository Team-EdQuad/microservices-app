from fastapi import APIRouter, HTTPException, status, Query
from app.utils.mongodb_connection import class_attendance_summery, student_attendance_summery
from datetime import datetime


async def fetch_attendance_ratio(subject_id: str, summary_type: str, class_id: str = None, student_id: str = None):
    if student_id:
        summary = await student_attendance_summery.find_one({"student_id": student_id})
    else:
        summary = await class_attendance_summery.find_one({"class_id": class_id})

    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class not found"
        )

    subject_record = next(
        (record for record in summary.get("attendance", []) if record["subject_id"] == subject_id),
        None
    )
    if not subject_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subject '{subject_id}' not found in class '{class_id}'."
        )

    today = datetime.now().strftime("%Y-%m-%d")

    if summary_type == "monthly":
        ratio = subject_record.get("current_month", {}).get("monthly_attendance_ratio", None)
    elif summary_type == "daily" and class_id:
        ratio = subject_record.get("current_month", {}).get("daily_attendance", {}).get(today, {}).get("ratio", None)
    elif summary_type == "yearly":
        ratio = subject_record.get("current_year", {}).get("yearly_attendance_ratio", None)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid summary_type. Choose from: monthly, daily, yearly."
        )

    if ratio is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No attendance ratio found for {summary_type} summary."
        )

    if student_id:
        return {
            "student_id": student_id,
            "subject_id": subject_id,
            "summary_type": summary_type,
            "attendance_ratio": ratio
        }
    else:
        return {
            "class_id": class_id,
            "subject_id": subject_id,
            "summary_type": summary_type,
            "attendance_ratio": ratio
        }
    

async def get_class_academic_ratio_service(class_id: str, subject_id: str, summary_type: str):
    try:
        result = await fetch_attendance_ratio(subject_id, summary_type, class_id=class_id)
        return {"data": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred in get_academic_ratio: {str(e)}"
        )


async def get_class_nonacademic_ratio_service(class_id: str, subject_id: str, summary_type: str):
    try:
        result = await fetch_attendance_ratio(subject_id, summary_type, class_id=class_id)
        return {"data": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred in get_nonacademic_ratio: {str(e)}"
        )


async def get_student_academic_ratio_service(student_id: str, subject_id: str, summary_type: str):
    try:
        result = await fetch_attendance_ratio(subject_id, summary_type, student_id=student_id)
        return {"data": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred in get_academic_ratio: {str(e)}"
        )


async def get_student_nonacademic_ratio_service(student_id: str, subject_id: str, summary_type: str):
    try:
        result = await fetch_attendance_ratio(subject_id, summary_type, student_id=student_id)
        return {"data": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred in get_nonacademic_ratio: {str(e)}"
        )
