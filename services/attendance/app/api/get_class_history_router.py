from fastapi import APIRouter, HTTPException, status, Query
from app.services.get_class_history_service import get_class_history_service

router = APIRouter(
    tags=["Class Attendance Summary"],
    prefix="/attendance"
)

@router.get("/history", status_code=status.HTTP_200_OK)
async def get_class_history_router(
    class_id: str = Query(..., description="Class ID"),
    subject_id: str = Query(..., description="Subject ID"),
    date: str = Query(..., description="date for the history"),
):
    """
    Fetches student data or attendance data based on whether it's already marked.
    """
    try:
        response = await get_class_history_service(class_id, subject_id, date)
        return response 

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )