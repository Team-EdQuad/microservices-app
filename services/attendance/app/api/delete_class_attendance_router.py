from fastapi import APIRouter, HTTPException, status
from app.services.delete_class_attendance_service import delete_class_attendance_service

router = APIRouter(
    tags=["Attendance Entry"],
    prefix="/attendance"
)

@router.delete("/delete-attendance-of-class/{attendance_id}", status_code=status.HTTP_200_OK)
async def delete_class_attendance_router(attendance_id: str):
    """
    Fetches student data or attendance data based on whether it's already marked.
    """
    try:
        response = await delete_class_attendance_service(attendance_id)
        return response
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

