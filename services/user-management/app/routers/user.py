from fastapi import APIRouter, Depends, HTTPException
from app.services.auth_service import get_current_user
from app.models.admin_model import AdminModel

router = APIRouter()

@router.get("/user-data")
async def get_user_data(current_user: AdminModel = Depends(get_current_user)):
    """Fetch role-based and user-specific content."""
    if current_user.role == "admin":
        # Fetch admin-specific data (for example, all users)
        return {"message": "Admin data", "data": {"admin_details": "All admins data here"}}
    elif current_user.role == "student":
        # Fetch student-specific data
        return {"message": "Student data", "data": {"student_details": f"Data for {current_user.first_name} {current_user.last_name}"}}
    elif current_user.role == "teacher":
        # Fetch teacher-specific data
        return {"message": "Teacher data", "data": {"teacher_details": f"Data for {current_user.first_name} {current_user.last_name}"}}
    else:
        raise HTTPException(status_code=403, detail="Access denied")
