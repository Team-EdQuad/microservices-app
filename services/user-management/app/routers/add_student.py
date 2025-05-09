from fastapi import APIRouter, HTTPException, Depends
from app.models.student_model import StudentRegistration
from app.services.student_service import register_student
from app.utils.auth import get_current_user  # Import the token verification function

router = APIRouter()

@router.post("/add-student")
async def add_student(
    student: StudentRegistration,
    current_user: dict = Depends(get_current_user)  # Enforce token validation
):
    # Check if the user has 'admin' role to add students
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Permission denied. Only admins can add students.")
    
    # If the user is an admin, proceed with the student registration process
    try:
        result = await register_student_service(student)  # Call the service function to add student
        return result
    except HTTPException as e:
        raise e
