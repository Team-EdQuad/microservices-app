from fastapi import APIRouter, HTTPException, status, Query
from app.services.get_attendance_ratio_service import get_class_academic_ratio_service, get_class_nonacademic_ratio_service, get_student_academic_ratio_service, get_student_nonacademic_ratio_service


classrouter = APIRouter(
    tags=["Class Attendance Summary"],
    prefix="/attendance/class"
)

# Academic endpoint
@classrouter.get("/academic/ratio", status_code=status.HTTP_200_OK)
async def get_academic_ratio(
    class_id: str = Query(..., description="Class ID"),
    subject_id: str = Query("academic", description="Subject ID"),
    summary_type: str = Query("monthly", description="Summary type: monthly, yearly, daily")
):
    """
    Fetches student data or attendance data based on whether it's already marked.
    """
    try:
        response = await get_class_academic_ratio_service(class_id, subject_id, summary_type)
        return response 

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )


# Non-academic endpoint
@classrouter.get("/nonacademic/ratio", status_code=status.HTTP_200_OK)
async def get_nonacademic_ratio(
    class_id: str = Query(..., description="Class ID"),
    subject_id: str = Query(..., description="Subject ID"),  # Note the required subject_id here
    summary_type: str = Query("monthly", description="Summary type: monthly, yearly, daily")
):
    """
    Fetches student data or attendance data based on whether it's already marked.
    """
    try:
        response = await get_class_nonacademic_ratio_service(class_id, subject_id, summary_type)
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


# Academic endpoint
@studentrouter.get("/academic/ratio", status_code=status.HTTP_200_OK)
async def get_academic_ratio(
    student_id: str = Query(..., description="Student ID"),
    subject_id: str = Query("academic", description="Subject ID"),
    summary_type: str = Query("monthly", description="Summary type: monthly, yearly")
):
    """
    Fetches student data or attendance data based on whether it's already marked.
    """
    try:
        response = await get_student_academic_ratio_service(student_id, subject_id, summary_type)
        return response 

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )
    

# Non-academic endpoint
@studentrouter.get("/nonacademic/ratio", status_code=status.HTTP_200_OK)
async def get_nonacademic_ratio(
    student_id: str = Query(..., description="Student ID"),
    subject_id: str = Query(..., description="Subject ID"),  # Note the required subject_id here
    summary_type: str = Query("monthly", description="Summary type: monthly, yearly")
):
    """
    Fetches student data or attendance data based on whether it's already marked.
    """
    try:
        response = await get_student_nonacademic_ratio_service(student_id, subject_id, summary_type)
        return response 

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )