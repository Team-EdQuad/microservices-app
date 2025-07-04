from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from app.utils.schemas import StudentsOfClassRequest
from app.services.get_class_students_service import get_class_students_service

router = APIRouter(
    tags=["Attendance Entry"],
    prefix="/attendance"
)

@router.post("/students/by-class", status_code=status.HTTP_200_OK)
async def get_class_students_router(request: StudentsOfClassRequest):
    """
    Fetches student data or attendance data based on whether it's already marked.
    """
    try:
        class_id = request.class_id
        subject_type = request.subject_type
        subject_id = request.subject_id
        date = request.date if request.date else datetime.now().strftime("%Y-%m-%d")

        response = await get_class_students_service(class_id, subject_type, subject_id, date)
        return response
    

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

