import httpx
from fastapi import HTTPException, Request
from typing import List, Dict, Any, Optional
from datetime import date

# CALENDAR_SERVICE_URL = "http://127.0.0.1:8007"
CALENDAR_SERVICE_URL = "http://calendar:8000"

async def get_assignment_deadlines(
    student_id: Optional[str] = None,
    class_id: Optional[str] = None,
    subject_id: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    authorization: str = None # Pass token if needed by calendar service
) -> List[Dict[str, Any]]:
    """
    Forwards the request to the Calendar microservice to fetch assignment deadlines.
    """
    params = {}
    if student_id:
        params["student_id"] = student_id
    if class_id:
        params["class_id"] = class_id
    if subject_id:
        params["subject_id"] = subject_id
    if start_date:
        params["start_date"] = start_date.isoformat() # Convert date to ISO format string
    if end_date:
        params["end_date"] = end_date.isoformat() # Convert date to ISO format string

    headers = {}
    if authorization:
        headers["Authorization"] = authorization

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{CALENDAR_SERVICE_URL}/assignments/deadlines",
                params=params,
                headers=headers
            )
            response.raise_for_status() # Raise an exception for 4xx or 5xx responses
            return response.json()
    except httpx.HTTPStatusError as e:
        print(f"Error from Calendar Service: {e.response.status_code} - {e.response.text}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Calendar Service error: {e.response.text}"
        )
    except httpx.RequestError as e:
        print(f"Network error communicating with Calendar Service: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Cannot connect to Calendar Service: {e}"
        )
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error when fetching calendar data: {str(e)}"
        )
