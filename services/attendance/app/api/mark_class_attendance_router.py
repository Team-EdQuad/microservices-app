from fastapi import APIRouter, HTTPException, status
from app.utils.schemas import AttendanceEntry
from app.services.mark_class_attendance_service import mark_class_attendance_service

router = APIRouter(
    tags=["Attendance Entry"],
    prefix="/attendance"
)

@router.post("/attendance_marking", status_code=status.HTTP_201_CREATED)
async def mark_class_attendance(new_attendance: AttendanceEntry):
    """
    Adds a new attendance record to the database.
    """
    try:
        response = await mark_class_attendance_service(
            class_id=new_attendance.class_id,
            subject_id=new_attendance.subject_id,
            date=new_attendance.date,
            status=new_attendance.status
        )
        return response

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

