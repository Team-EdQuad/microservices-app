from fastapi import APIRouter, HTTPException, Depends
from app.models.student_model import StudentRegistration
from app.services.student_service import register_student
# from app.utils.auth import get_current_user  # Import the token verification function
from app.services.auth_service import get_current_user

from app.models.admin_model import AdminModel
router = APIRouter()

# @router.post("/add-student")
# async def add_student(
#     student: StudentRegistration,
#     current_user = Depends(get_current_user)  # Enforce token validation
# ):
#     # Check if the user has 'admin' role to add students
#     if getattr(current_user, "role", None) != "admin":
#         raise HTTPException(status_code=403, detail="Permission denied. Only admins can add students.")
    
#     # If the user is an admin, proceed with the student registration process
#     try:
#         result = await register_student(student)  # Call the service function to add student
#         return result
#     except HTTPException as e:
#         raise e

@router.post("/add-student")
async def add_student(
    student: StudentRegistration,
    current_user: AdminModel = Depends(get_current_user)  # type hint for better clarity
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied. Only admins can add students.")
<<<<<<< HEAD
    
    # If the user is an admin, proceed with the student registration process
    try:
        result = await register_student_service(student)  # Call the service function to add student
        return result
    except HTTPException as e:
        raise e


async def post_add_student(student_data: dict, request: Request):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{USER_MANAGEMENT_SERVICE_URL}/add-student",
                json=student_data,
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
        raise HTTPException(status_code=500, detail=f"Error adding student: {str(exc)}")
=======
    result = await register_student(student)
    return result
>>>>>>> dev
