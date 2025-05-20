from fastapi import APIRouter, HTTPException, status, Query
from app.services.get_attendance_summary_service import get_class_academic_summary_service, get_class_nonacademic_summary_service, get_student_academic_summary_service, get_student_nonacademic_summary_service

classrouter = APIRouter(
    tags=["Class Attendance Summary"],
    prefix="/attendance/class"
)


@classrouter.get("/academic/summary", status_code=status.HTTP_200_OK)
async def get_academic_summary(
    class_id: str = Query(..., description="Class ID"),
    subject_id: str = Query("academic", description="Subject ID"),
    summary_type: str = Query("monthly", description="Summary type: monthly, weekly, daily"),
    month: str = Query(None, description="Month for the summary_type"),
):
    """
    Fetches student data or attendance data based on whether it's already marked.
    """
    try:
        response = await get_class_academic_summary_service(class_id, subject_id, summary_type, month)
        return response 

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )
    

@classrouter.get("/nonacademic/summary", status_code=status.HTTP_200_OK)
async def get_nonacademic_summary(
    class_id: str = Query(..., description="Class ID"),
    subject_id: str = Query(..., description="Subject ID"),
    summary_type: str = Query("monthly", description="Summary type: monthly, weekly, daily"),
    month: str = Query(None, description="Month for the summary_type"),
):
    """
    Fetches student data or attendance data based on whether it's already marked.
    """
    try:
        response = await get_class_nonacademic_summary_service(class_id, subject_id, summary_type, month)
        return response 

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )
    

studentrouter = APIRouter(
    tags=["Student Attendance Summary"],
    prefix="/attendance/student"
)


@studentrouter.get("/academic/summary", status_code=status.HTTP_200_OK)
async def get_academic_ratio(
    student_id: str = Query(..., description="Student ID"),
    subject_id: str = Query("academic", description="Subject ID"),
    summary_type: str = Query("monthly", description="Summary type: monthly, weekly, daily"),
    month: str = Query(None, description="Month for the summary_type"),
):
    """
    Fetches student data or attendance data based on whether it's already marked.
    """
    try:
        response = await get_student_academic_summary_service(student_id, subject_id, summary_type, month)
        return response 

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )
    

@studentrouter.get("/nonacademic/summary", status_code=status.HTTP_200_OK)
async def get_nonacademic_ratio(
    student_id: str = Query(..., description="Student ID"),
    subject_id: str = Query(..., description="Subject ID"),
    summary_type: str = Query("monthly", description="Summary type: monthly, weekly, daily"),
    month: str = Query(None, description="Month for the summary_type"),
):
    """
    Fetches student data or attendance data based on whether it's already marked.
    """
    try:
        response = await get_student_nonacademic_summary_service(student_id, subject_id, summary_type, month)
        return response 

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )