from fastapi import APIRouter, HTTPException, status
from app.services.medical_delete_service import medical_delete_service

router = APIRouter(
    tags=["Medical Related Documents"],
    prefix="/attendance"
)

@router.delete("/delete/document/{document_id}", status_code=status.HTTP_200_OK)
async def medical_delete_router(document_id: str):
    """
    Fetches student data or attendance data based on whether it's already marked.
    """
    try:
        response = await medical_delete_service(document_id)
        return response
    

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )
    
