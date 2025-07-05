from fastapi import APIRouter, Depends, HTTPException
from app.services.auth_service import get_current_user
from app.models.admin_model import AdminModel

router = APIRouter()

# Your existing /profile endpoint (keep as is)
@router.get("/profile")
async def get_user_profile(current_user: AdminModel = Depends(get_current_user)):
    """Fetch role-based and user-specific content."""
    profile_data = {}

    if current_user.role == "admin":
        profile_data = current_user.dict()
    elif current_user.role == "student":
        profile_data = {
            "role": "student",
            "student_id": current_user.student_id,
            "full_name": current_user.full_name,
            "email": current_user.email,
            "class_id": current_user.class_id,
            "subjects": current_user.subject,
            "phone": current_user.phone
        }
    elif current_user.role == "teacher":
        profile_data = {
            "role": "teacher",
            "teacher_id": current_user.teacher_id,
            "full_name": current_user.full_name,
            "email": current_user.email,
            "gender": current_user.gender,
            "subjects_classes": current_user.subjects_classes,
            "phone": current_user.phone
        }
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied: Unknown role")

    if not profile_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile data not found for this user.")

    print("DEBUG returning user:", profile_data)
    return profile_data

# NEW: Admin Delete User Endpoint
@router.delete("/delete-user/{role}/{user_custom_id}")
async def delete_user_by_admin(
    role: str,
    user_custom_id: str,
    current_user: AdminModel = Depends(get_current_user) # Ensure only admins can call this
):
    """
    Admin endpoint to delete a user by role and their custom ID.
    Requires admin privileges.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete users."
        )

    try:
        success = await admin_delete_user_by_custom_id(role, user_custom_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID '{user_custom_id}' not found in role '{role}'."
            )
        return {"message": f"User '{user_custom_id}' of role '{role}' deleted successfully."}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {e}")
