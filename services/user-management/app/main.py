from fastapi import FastAPI, Depends, HTTPException
from app.routers import login, add_admin, add_student, add_teacher,delete_user,edit_profile,update_password, admin_user_management
from app.services.auth_service import get_current_user
from app.models.admin_model import AdminModel

app = FastAPI(title="User Management")

# Include routers for each functionality
app.include_router(login.router)
app.include_router(add_admin.router)
app.include_router(add_student.router)
app.include_router(add_teacher.router)
# app.include_router(delete_user.router)
app.include_router(admin_user_management.router)
app.include_router(edit_profile.router)
app.include_router(update_password.router)


@app.get("/profile")
async def get_profile(current_user=Depends(get_current_user)):
    role = current_user.role.lower()

    id_field_map = {
        "admin": "admin_id",
        "teacher": "teacher_id",
        "student": "student_id"
    }
    id_field = id_field_map.get(role)
    if not id_field:
        raise HTTPException(status_code=400, detail="Invalid user role")

    user_id = getattr(current_user, id_field, None)
    if user_id is None:
        raise HTTPException(status_code=404, detail="User ID not found")

    full_name = getattr(current_user, "full_name", "").strip()
    if not full_name or full_name.lower() == "string":
        first = getattr(current_user, "first_name", "").strip()
        last = getattr(current_user, "last_name", "").strip()
        full_name = f"{first} {last}".strip()
        
    profile_data = {
        "user_id": user_id,
        "role": current_user.role,
        "full_name": full_name,
    }
    if role == "student":
        profile_data["class_id"] = getattr(current_user, "class_id", None)

    return profile_data