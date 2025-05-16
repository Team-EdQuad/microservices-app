from fastapi import APIRouter, HTTPException, status, Query
from app.services.get_medicals_service import get_medicals_service

router = APIRouter(
    tags=["Medical Related Documents"],
    prefix="/attendance"
)

@router.get("/documents", status_code=status.HTTP_200_OK)
async def get_medicals_router(
    class_id: str = Query("all", description="Class ID"),
    subject_id: str = Query("all", description="Subject ID"),
    student_id: str = Query("all", description="Student ID"),
):
    """
    Fetches student data or attendance data based on whether it's already marked.
    """
    try:
        response = await get_medicals_service(class_id, subject_id, student_id)
        return response
    

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )