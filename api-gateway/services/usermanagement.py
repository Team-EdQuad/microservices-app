import httpx
from fastapi import HTTPException, Request, APIRouter, Depends
from typing import Optional
import json
from datetime import date
# from app.services.auth_service import get_current_user
# from app.models.admin_model import AdminModel

# USER_MANAGEMENT_SERVICE_URL = "http://127.0.0.1:8001"

USER_MANAGEMENT_SERVICE_URL = "http://user-management:8000"

router = APIRouter()

# --- Login ---
# async def login_user(credentials: dict):
#     try:
#         async with httpx.AsyncClient() as client:
#             response = await client.post(
#                 f"{USER_MANAGEMENT_SERVICE_URL}/login",
#                 json=credentials
#             )
#             response.raise_for_status()
#             return response.json()
#     except httpx.HTTPStatusError as exc:
#         raise HTTPException(status_code=exc.response.status_code, detail="Login failed")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
#     raise HTTPException(status_code=500, detail=str(e))
async def login_user(credentials: dict):
    try:
        async with httpx.AsyncClient() as client:
            # Send as form data instead of JSON
            response = await client.post(
                f"{USER_MANAGEMENT_SERVICE_URL}/login",
                data=credentials  # Changed from json= to data=
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        print("Status code:", exc.response.status_code)
        print("Response text:", exc.response.text)
        raise HTTPException(status_code=exc.response.status_code, detail="Login failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Add Admin ---
async def add_admin(admin_data: dict, authorization: str = None):
    headers = {}
    if authorization:
        headers["Authorization"] = authorization

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{USER_MANAGEMENT_SERVICE_URL}/add-admin",
                json=admin_data,
                headers=headers  # only include if authorization is not None
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        detail = exc.response.json().get("detail", "User service error")
        raise HTTPException(status_code=exc.response.status_code, detail=detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Add Student ---
def serialize_dates(data: dict):
    for key, value in data.items():
        if isinstance(value, date):
            data[key] = value.isoformat()
        elif isinstance(value, list):
            # Recursively check lists for dates (e.g. club_id or sport_id might be empty, but if they had dates)
            data[key] = [v.isoformat() if isinstance(v, date) else v for v in value]
    return data

async def add_student(student_data: dict, authorization: str = None):
    headers = {}
    if authorization:
        headers["Authorization"] = authorization

    # Serialize date fields to string
    student_data = serialize_dates(student_data)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{USER_MANAGEMENT_SERVICE_URL}/add-student",
                json=student_data,
                headers=headers
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        detail = exc.response.json().get("detail", "User service error")
        raise HTTPException(status_code=exc.response.status_code, detail=detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Add Teacher ---
async def add_teacher(teacher_data: dict, authorization: str = None):
    headers = {}
    if authorization:
        headers["Authorization"] = authorization

    teacher_data = serialize_dates(teacher_data)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{USER_MANAGEMENT_SERVICE_URL}/add-teacher",
                json=teacher_data,
                headers=headers
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        detail = exc.response.json().get("detail", "User service error")
        raise HTTPException(status_code=exc.response.status_code, detail=detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Delete User ---
async def delete_user(role: str, user_custom_id: str, authorization: str = None):
    headers = {}
    if authorization:
        headers["Authorization"] = authorization

    url = f"{USER_MANAGEMENT_SERVICE_URL}/delete_user/{role}/{user_custom_id}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(url, headers=headers)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        detail = exc.response.json().get("detail", "User service error")
        raise HTTPException(status_code=exc.response.status_code, detail=detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# --- Edit Profile ---
async def edit_profile(role: str, user_id: str, profile_data: dict, authorization: str = None):
    headers = {}
    if authorization:
        headers["Authorization"] = authorization

    url = f"{USER_MANAGEMENT_SERVICE_URL}/edit_profile/{role}/{user_id}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(url, json=profile_data, headers=headers)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        detail = exc.response.json().get("detail", "User service error")
        raise HTTPException(status_code=exc.response.status_code, detail=detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# --- Update Password ---
async def update_password(password_data: dict, authorization: str = None):
    headers = {}
    if authorization:
        headers["Authorization"] = authorization

    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{USER_MANAGEMENT_SERVICE_URL}/update_password",
                json=password_data,
                headers=headers
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        detail = exc.response.json().get("detail", "User service error")
        raise HTTPException(status_code=exc.response.status_code, detail=detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# # --- Get Profile ---
# async def get_profile(authorization: Optional[str] = None):
#     headers = {}
#     if authorization:
#         headers["Authorization"] = authorization

#     try:
#         async with httpx.AsyncClient() as client:
#             response = await client.get(
#                 f"{USER_MANAGEMENT_SERVICE_URL}/profile",
#                 headers=headers
#             )
#             response.raise_for_status()
#             return response.json()
#     except httpx.HTTPStatusError as exc:
#         detail = exc.response.json().get("detail", "User service error")
#         raise HTTPException(status_code=exc.response.status_code, detail=detail)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# --- Get Profile ---
async def get_profile(authorization: Optional[str] = None):
    headers = {}
    if authorization:
        headers["Authorization"] = authorization

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{USER_MANAGEMENT_SERVICE_URL}/profile",
                headers=headers
            )
            response.raise_for_status()
            return response.json()

    except httpx.HTTPStatusError as exc:
        try:
            detail = exc.response.json().get("detail", "User service error")
        except Exception:
            # Handles case where response body is not JSON or empty
            detail = f"User service error: {exc.response.text or 'Empty response'}"
        raise HTTPException(status_code=exc.response.status_code, detail=detail)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def serialize_dates(data: dict):
    for key, value in data.items():
        if isinstance(value, date):
            data[key] = value.isoformat()
        elif isinstance(value, list):
            data[key] = [v.isoformat() if isinstance(v, date) else v for v in value]
    return data