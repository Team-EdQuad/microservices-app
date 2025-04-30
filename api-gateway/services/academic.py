import httpx
from fastapi import HTTPException
ACADEMIC_SERVICE_URL = "http://127.0.0.1:8002"

async def get_subject_names(student_id: str):
    """
    Fetch the list of subjects for a given student by calling the academic service.
    """
    try:
        async with httpx.AsyncClient() as client:
            url = f"{ACADEMIC_SERVICE_URL}/students/{student_id}/subjects"
            response = await client.get(url)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.json()  # Return the JSON response
    except httpx.HTTPStatusError as exc:
        # Handle HTTP errors (e.g., 404, 500)
        raise HTTPException(status_code=exc.response.status_code, detail=f"HTTP error: {exc.response.text}")
    except Exception as exc:
        # Handle other exceptions (e.g., network issues)
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(exc)}")
    
    
async def get_student_content(student_id: str, subject_id: str):
    try:
        async with httpx.AsyncClient() as client:
            url = f"{ACADEMIC_SERVICE_URL}/content/{student_id}/{subject_id}"
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=f"HTTP error: {exc.response.text}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error fetching content: {str(exc)}")

async def get_all_assignments(student_id: str, subject_id: str):
    try:
        async with httpx.AsyncClient() as client:
            url = f"{ACADEMIC_SERVICE_URL}/show_assignments/{student_id}/{subject_id}"
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=f"HTTP error: {exc.response.text}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error fetching assignments: {str(exc)}")