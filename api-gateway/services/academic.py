import os
import httpx
from fastapi import HTTPException, UploadFile
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
    
async def get_assignment_by_id(assignment_id: str):
    try:
        async with httpx.AsyncClient() as client:
            url = f"{ACADEMIC_SERVICE_URL}/assignment/{assignment_id}"
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=f"HTTP error: {exc.response.text}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error fetching assignment: {str(exc)}")


async def get_assignment_marks(student_id: str):
    try:
        async with httpx.AsyncClient() as client:
            url = f"{ACADEMIC_SERVICE_URL}/submissionmarks/{student_id}"
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=f"HTTP error: {exc.response.text}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error fetching assignment marks: {str(exc)}")


async def get_exam_marks(student_id: str):
    try:
        async with httpx.AsyncClient() as client:
            url = f"{ACADEMIC_SERVICE_URL}/exammarks/{student_id}"
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=f"HTTP error: {exc.response.text}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error fetching exam marks: {str(exc)}")


async def upload_assignment_file(student_id: str, assignment_id: str, file: UploadFile):
    try:
        async with httpx.AsyncClient() as client:
            files = {"file": (file.filename, await file.read(), file.content_type)}
            url = f"{ACADEMIC_SERVICE_URL}/submission/{student_id}/{assignment_id}"
            response = await client.post(url, files=files)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=f"HTTP error: {exc.response.text}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Submission failed: {str(exc)}")


async def mark_content_done(content_id: str):
    try:
        async with httpx.AsyncClient() as client:
            url = f"{ACADEMIC_SERVICE_URL}/content/{content_id}"
            response = await client.post(url)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=f"HTTP error: {exc.response.text}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to update content status: {str(exc)}")
