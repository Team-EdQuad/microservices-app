import httpx
from fastapi import HTTPException

ACADEMIC_SERVICE_URL = "http://127.0.0.1:8002"

async def get_subject_names(student_id: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{ACADEMIC_SERVICE_URL}/students/{student_id}/subjects")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error fetching subjects: {str(exc)}")


async def get_content_details(student_id, subject_id):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{ACADEMIC_SERVICE_URL}/students/{student_id}/subjects/{subject_id}/content")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error fetching content: {str(exc)}")





NON_ACADEMIC_SERVICE_URL = "http://127.0.0.1:8003" 
async def get_all_sports():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{NON_ACADEMIC_SERVICE_URL}/sports/")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error fetching sports: {str(exc)}")
