import httpx
from fastapi import HTTPException

# NON_ACADEMIC_SERVICE_URL = "http://127.0.0.1:8003"

NON_ACADEMIC_SERVICE_URL = "http://non-academic:8000"

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

async def create_sport(sport: dict):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{NON_ACADEMIC_SERVICE_URL}/sports/", json=sport)
            response.raise_for_status()
            return response.json()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error creating sport: {str(exc)}")
    
async def filter_sports(type: str = None, category: str = None):
    try:
        async with httpx.AsyncClient() as client:
            params = {}
            if type:
                params["type"] = type
            if category:
                params["category"] = category
            response = await client.get(f"{NON_ACADEMIC_SERVICE_URL}/sports/filter/", params=params)
            response.raise_for_status()
            return response.json()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error filtering sports: {str(exc)}")

async def get_all_clubs():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{NON_ACADEMIC_SERVICE_URL}/clubs/")
            response.raise_for_status()
            return response.json()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error fetching clubs: {str(exc)}")

async def create_club(club: dict):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{NON_ACADEMIC_SERVICE_URL}/clubs/", json=club)
            response.raise_for_status()
            return response.json()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error creating club: {str(exc)}")