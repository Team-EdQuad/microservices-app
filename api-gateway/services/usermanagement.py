# import httpx
# from fastapi import HTTPException

# USER_MANAGEMENT_SERVICE_URL = "http://127.0.0.1:8001"


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
#      raise HTTPException(status_code=500, detail=str(e))
    
import httpx
from fastapi import HTTPException, Request, APIRouter, Depends
from typing import Optional
# from app.services.auth_service import get_current_user
# from app.models.admin_model import AdminModel

USER_MANAGEMENT_SERVICE_URL = "http://127.0.0.1:8001"

router = APIRouter()

# --- Login ---
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
    raise HTTPException(status_code=500, detail=str(e))

# --- Add Admin ---
async def post_add_admin(admin_data: dict, request: Request):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{USER_MANAGEMENT_SERVICE_URL}/add-admin",
                json=admin_data,
                headers={
                    "Authorization": request.headers.get("authorization", ""),
                    "User-Agent": request.headers.get("user-agent", "")
                }
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error posting admin: {str(exc)}")

# --- Add Teacher ---
async def post_add_teacher(teacher_data: dict, authorization: Optional[str] = None):
    try:
        headers = {"Authorization": authorization} if authorization else {}
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{USER_MANAGEMENT_SERVICE_URL}/add-teacher",
                json=teacher_data,
                headers=headers
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error adding teacher: {str(exc)}")

# --- Delete User ---
async def post_delete_user(user_data: dict, request: Request):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{USER_MANAGEMENT_SERVICE_URL}/delete_user",
                json=user_data,
                headers={"Authorization": request.headers.get("authorization", "")}
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error deleting user: {str(exc)}")

# --- Edit Profile ---
async def put_edit_profile(email: str, profile_data: dict, authorization: Optional[str] = None):
    try:
        headers = {"Authorization": authorization} if authorization else {}
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{USER_MANAGEMENT_SERVICE_URL}/edit_profile/{email}",
                json=profile_data,
                headers=headers
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error editing profile: {str(exc)}")

# --- Update Password ---
async def put_update_password(password_data: dict, authorization: Optional[str] = None):
    try:
        headers = {"Authorization": authorization} if authorization else {}
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{USER_MANAGEMENT_SERVICE_URL}/update_password",
                json=password_data,
                headers=headers
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error updating password: {str(exc)}")

# --- Get Role-based User Data ---
async def get_current_user(request: Request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        raise HTTPException(status_code=401, detail="Authorization token missing")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{USER_MANAGEMENT_SERVICE_URL}/verify-token",
                headers={"Authorization": f"Bearer {token}"}
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error verifying token: {str(exc)}")
# async def get_user_data(current_user: AdminModel = Depends(get_current_user)):
#     """
#     Fetch role-based and user-specific content from the user management microservice.
#     """
#     try:
#         async with httpx.AsyncClient() as client:
#             if current_user.role == "admin":
#                 # Call microservice to get all admin data
#                 response = await client.get(
#                     f"{USER_MANAGEMENT_SERVICE_URL}/admin-details",
#                     headers={"Authorization": f"Bearer {current_user.token}"}
#                 )
#                 response.raise_for_status()
#                 admin_data = response.json()
#                 return {"message": "Admin data", "data": admin_data}

#             elif current_user.role == "student":
#                 return {
#                     "message": "Student data",
#                     "data": {
#                         "student_details": f"Data for {current_user.first_name} {current_user.last_name}"
#                     }
#                 }

#             elif current_user.role == "teacher":
#                 return {
#                     "message": "Teacher data",
#                     "data": {
#                         "teacher_details": f"Data for {current_user.first_name} {current_user.last_name}"
#                     }
#                 }

#             else:
#                 raise HTTPException(status_code=403, detail="Access denied")
#     except httpx.HTTPStatusError as exc:
#         raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
#     except Exception as exc:
#         raise HTTPException(status_code=500, detail=f"Error fetching user data: {str(exc)}")