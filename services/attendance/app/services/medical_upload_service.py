from fastapi import APIRouter, HTTPException, status
from app.services.background_services.medical_upload_to_cloud import medical_upload_to_cloud
from fastapi import UploadFile
from app.utils.schemas import DocumentUpload
from app.utils.mongodb_connection import document_store
import io  # Import BytesIO


async def medical_upload_service(file: UploadFile, student_id: str, class_id: str, subject_id: str, date: str):
    """
    Upload new document for absent dates
    """
    try:
        allowed_types = {
            "application/pdf": "pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation": "pptx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
        }

        file_type = allowed_types.get(file.content_type)
        if not file_type:
            return {"error": "Invalid file type"}

        # Convert UploadFile to BytesIO for compatibility with S3
        file_content = await file.read()
        file_like_object = io.BytesIO(file_content)

        # Upload to S3
        file_url = medical_upload_to_cloud(file_like_object, file.filename, file.content_type)
        if not file_url:
            return {"error": "Failed to upload to S3"}

        # Create DocumentUpload model
        document = DocumentUpload(
            student_id=student_id,
            class_id=class_id,
            subject_id=subject_id,
            date=date,
            file_path=file_url,
            file_name=file.filename,
            file_type=file_type,
            is_checked=False,
        )

        await document_store.insert_one(document.model_dump())

        return {"message": "File uploaded successfully", "data": document.dict()}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

