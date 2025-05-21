from fastapi import APIRouter, HTTPException, status, Query
from app.services.get_nonacadamic_subjects_service import (
    get_all_nonacadamic_subjects_service,
    get_student_nonacadamic_subjects_service
)


studentrouter = APIRouter(
    tags=["Non-Acadamic Subjects"],
    prefix="/attendance/non-acadamic"
)

# First route - student-specific non-academic subjects
@studentrouter.get("/subjects/{student_id}", summary="Get all non-academic subject IDs for a student")
async def get_student_nonacadamic_subjects_router(student_id: str):
    """
    Fetches student data or attendance data based on whether it's already marked.
    """
    try:
        response = await get_student_nonacadamic_subjects_service(student_id)
        return response 

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

    

allrouter = APIRouter(
    tags=["Non-Acadamic Subjects"],
    prefix="/attendance/non-acadamic"
)

# Second route - all available non-academic subjects
@allrouter.get("/subjects", summary="Get all non-academic subject IDs from sports and clubs collection")
async def get_all_nonacadamic_subjects_router():
    """
    Fetches student data or attendance data based on whether it's already marked.
    """
    try:
        response = await get_all_nonacadamic_subjects_service()
        return response 

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )