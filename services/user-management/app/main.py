from fastapi import FastAPI, Depends, HTTPException
from app.routers import login, add_admin, add_student, add_teacher,delete_user,edit_profile,update_password
from app.services.auth_service import get_current_user
from app.models.admin_model import AdminModel

app = FastAPI(title="User Management")

# Include routers for each functionality
app.include_router(login.router)
app.include_router(add_admin.router)
app.include_router(add_student.router)
app.include_router(add_teacher.router)
app.include_router(delete_user.router)
app.include_router(edit_profile.router)
app.include_router(update_password.router)



@app.get("/user-data")
async def get_user_data(current_user: AdminModel = Depends(get_current_user)):
    """Fetch role-based and user-specific content."""
    if current_user.role == "admin":
        # Admin-specific data
        return {"message": "Admin data", "data": {"admin_details": "All admins data here"}}
    elif current_user.role == "student":
        # Student-specific data
        return {"message": "Student data", "data": {"student_details": f"Data for {current_user.first_name} {current_user.last_name}"}}
    elif current_user.role == "teacher":
        # Teacher-specific data
        return {"message": "Teacher data", "data": {"teacher_details": f"Data for {current_user.first_name} {current_user.last_name}"}}
    else:
        raise HTTPException(status_code=403, detail="Access denied")
