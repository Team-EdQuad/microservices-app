from fastapi import HTTPException, status
from app.utils.mongodb_connection import document_store
from bson import ObjectId
from app.services.background_services.delete_medical_from_cloud import delete_medical_from_cloud

async def medical_delete_service(document_id: str):
    try:
        # Step 1: Find document first
        document = await document_store.find_one({"_id": ObjectId(document_id)})

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )

        s3_url = document.get("file_path")
        if not s3_url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File path is missing in the document"
            )

        # Step 2: Delete from S3
        await delete_medical_from_cloud(s3_url)

        # Step 3: Delete from MongoDB
        result = await document_store.delete_one({"_id": ObjectId(document_id)})

        return {"message": "Document and file deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting document: {str(e)}"
        )

