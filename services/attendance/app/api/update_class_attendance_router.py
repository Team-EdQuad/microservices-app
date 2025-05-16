from fastapi import APIRouter, HTTPException, status
from app.utils.schemas import AttendanceEntry
from app.services.update_class_attendance_service import update_class_attendance_service

router = APIRouter(
    tags=["Attendance Entry"],
    prefix="/attendance"
)

@router.put("/update_attendance_of_class/{attendance_id}", status_code=status.HTTP_202_ACCEPTED)
async def update_class_attendance_service_route(attendance_id: str, updated_attendance: AttendanceEntry):
    """
    Updates an existing attendance record with the latest status and weekday information.
    """
    try:
        # Extract the necessary fields from the `updated_attendance` model
        class_id = updated_attendance.class_id
        subject_id = updated_attendance.subject_id
        date = updated_attendance.date
        status = updated_attendance.status

        # Call the service function with extracted parameters
        response = await update_class_attendance_service(
            attendance_id=attendance_id,
            class_id=class_id,
            subject_id=subject_id,
            date=date,
            status=status
        )
        return response

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )
