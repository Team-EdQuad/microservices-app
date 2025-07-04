# from fastapi import APIRouter, Depends, HTTPException
# from app.services.auth_service import get_current_user
# from app.models.admin_model import AdminModel

# router = APIRouter()

# @router.get("/profile")
# async def get_user_data(current_user: AdminModel = Depends(get_current_user)):
#     """Fetch role-based and user-specific content."""
#     if current_user.role == "admin":
#         # Fetch admin-specific data (for example, all users)
#         return {"message": "Admin data", "data": {"admin_details": "All admins data here"}}
#     elif current_user.role == "student":
#         # Fetch student-specific data
#         return {"message": "Student data", "data": {"student_details": f"Data for {current_user.first_name} {current_user.last_name}"}}
#     elif current_user.role == "teacher":
#         # Fetch teacher-specific data
#         return {"message": "Teacher data", "data": {"teacher_details": f"Data for {current_user.first_name} {current_user.last_name}"}}
#     else:
#         raise HTTPException(status_code=403, detail="Access denied")


# user-management/app/routers/users.py

from fastapi import APIRouter, Depends, HTTPException
from app.models.admin_model import AdminModel # Or a more generic User type from your models

router = APIRouter()

# CHANGE /user-data to /profile to match the API Gateway
@router.get("/profile") # <--- Changed this line
async def get_user_profile(current_user: AdminModel = Depends(get_current_user)):
    """Fetch role-based and user-specific content."""

    profile_data = {} # Initialize empty dict for profile

    if current_user.role == "admin":
        profile_data = current_user.dict()
        # profile_data = {
        #     "role": "admin",
        #     "admin_id": current_user.admin_id, # Assuming AdminModel has admin_id
        #     "full_name": current_user.full_name, # Assuming AdminModel has full_name
        #     "email": current_user.email,
        #     "gender": current_user.gender,
        #     "join_date": current_user.join_date,
        #     "phone": current_user.phone
        #     # ... include all fields you want for admin profile
        # }
    elif current_user.role == "student":
        # Fetch actual student data from your DB based on current_user.student_id
        # Example:
        # from app.db.student_crud import get_student_by_id
        # profile_data = await get_student_by_id(current_user.student_id)
        profile_data = {
            "role": "student",
            "student_id": current_user.student_id, # Assuming StudentModel passed to current_user
            "full_name": current_user.full_name,
            "email": current_user.email,
            "class_id": current_user.class_id,
            "subjects": current_user.subject, # Assuming 'subject' field in your StudentRegistration model
            "phone": current_user.phone
            # ... include all fields for student profile
        }
    elif current_user.role == "teacher":
        # Fetch actual teacher data from your DB based on current_user.teacher_id
        # Example:
        # from app.db.teacher_crud import get_teacher_by_id
        # profile_data = await get_teacher_by_id(current_user.teacher_id)
        profile_data = {
            "role": "teacher",
            "teacher_id": current_user.teacher_id, # Assuming TeacherModel passed to current_user
            "full_name": current_user.full_name,
            "email": current_user.email,
            "gender": current_user.gender,
            "subjects_classes": current_user.subjects_classes,
            "phone": current_user.Phone_no # Note the 'Phone_no' casing
            # ... include all fields for teacher profile
        }
    else:
        raise HTTPException(status_code=403, detail="Access denied: Unknown role")

    if not profile_data:
        raise HTTPException(status_code=404, detail="Profile data not found for this user.")
    

    print("DEBUG returning user:", profile_data)
    return profile_data


