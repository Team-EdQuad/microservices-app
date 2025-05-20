from fastapi import APIRouter, HTTPException, status, UploadFile, Form, File
from datetime import datetime
from app.services.medical_upload_service import medical_upload_service

router = APIRouter(
    tags=["Medical Related Documents"],
    prefix="/attendance"
)

@router.post("/document-upload", status_code=status.HTTP_201_CREATED)
async def medical_upload_router(
    file: UploadFile = File(...),
    student_id: str = Form(...),
    class_id: str = Form(...),
    subject_id: str = Form("academic"),
    date: str = Form(datetime.now().strftime("%Y-%m-%d")),
):
    """
    Fetches student data or attendance data based on whether it's already marked.
    """
    try:
        response = await medical_upload_service(file, student_id, class_id, subject_id, date)
        return response 

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )