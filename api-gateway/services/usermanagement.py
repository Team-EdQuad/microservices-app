import httpx
from fastapi import HTTPException, Request, APIRouter, Depends, UploadFile
from typing import Optional,Dict, Any
from pathlib import Path 
import json
from datetime import date
import shutil
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from fastapi import Query



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user-management/login")

# from app.services.auth_service import get_current_user
# from app.models.admin_model import AdminModel

USER_MANAGEMENT_SERVICE_URL = "http://127.0.0.1:8001"


router = APIRouter()


# --- Login ---
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


# --- Logout ---
async def logout_user(user_id: str, role: str, authorization: str = None):
    headers = {}
    if authorization:
        headers["Authorization"] = authorization

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{USER_MANAGEMENT_SERVICE_URL}/logout",
                data={"user_id": user_id, "role": role},
                headers=headers
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        detail = exc.response.json().get("detail", "User service error")
        raise HTTPException(status_code=exc.response.status_code, detail=detail)
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

# NEW: Function to call the internal recent users endpoint
async def get_recent_users_from_user_management(role: str, authorization: str = None):
    headers = {}
    if authorization:
        headers["Authorization"] = authorization

    url = f"{USER_MANAGEMENT_SERVICE_URL}/recent-users/{role}" # New internal path

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
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

# ... (other existing functions in usermanagement.py) ...    
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

# @router.get("/api/anomaly-detection/results")
async def fetch_anomaly_results(
    # If 'authorization' is truly a distinct, required header passed here,
    # it would go here as well, before any optional arguments.
    # If not used, keep it removed as per previous suggestion.
    username: Optional[str] = None, # Now, optional arguments with defaults
    role: Optional[str] = None,
    token: Optional[str] = None,
):
    headers = {"Authorization": f"Bearer {token}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{USER_MANAGEMENT_SERVICE_URL}/anomaly-detection/results",
                params={"username": username, "role": role},
                headers=headers
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        # Return the actual response content from the service
        detail = exc.response.text
        print(f"HTTPStatusError: {detail}")
        raise HTTPException(status_code=exc.response.status_code, detail=detail)
    except Exception as e:
        print(f"Unexpected error in fetch_anomaly_results: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))




# @router.get("/anomaly-detection/results")
# async def get_anomaly_results(
#     username: Optional[str] = Query(None),
#     role: Optional[str] = Query(None),
#     current_user=Depends(get_current_user)
# ):
#     try:
#         if current_user.role != "admin":
#             raise HTTPException(status_code=403, detail="Only admins can access anomaly results")

#         db = get_database()
#         query = {}

#         if username:
#             query["username"] = username
#         if role:
#             query["role"] = role

#         cursor = db["login_anomaly_results"].find(query).sort("timestamp", -1)
#         results = []
#         async for doc in cursor:
#             doc["_id"] = str(doc["_id"])  # Convert ObjectId to string
#             results.append(doc)

#         return {"results": results}
#     except Exception as e:
#         # Log the exception to console or file for debugging
#         print("Exception in anomaly results endpoint:", e)
#         raise HTTPException(status_code=500, detail=str(e))
