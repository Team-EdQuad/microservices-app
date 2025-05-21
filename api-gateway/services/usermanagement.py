import httpx
from fastapi import HTTPException, Request, APIRouter, Depends
from typing import Optional

USER_MANAGEMENT_SERVICE_URL = "http://127.0.0.1:8001"


async def login_user(credentials: dict):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{USER_MANAGEMENT_SERVICE_URL}/login",
                json=credentials
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail="Login failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
