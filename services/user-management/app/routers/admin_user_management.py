from fastapi import APIRouter, Depends, HTTPException
from app.services.auth_service import get_current_user
from app.db.database import db

router = APIRouter()

@router.delete("/delete_user/{role}/{user_custom_id}")
async def delete_user_by_admin(role: str, user_custom_id: str, current_user=Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete users")

    valid_roles = {
        "student": "student_id",
        "teacher": "teacher_id",
        "admin": "admin_id"
    }

    if role not in valid_roles:
        raise HTTPException(status_code=400, detail="Invalid role")

    field_name = valid_roles[role]

    result = await db[role].delete_one({field_name: user_custom_id})

    if result.deleted_count == 1:
        return {"message": f"{role.capitalize()} deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail=f"{role.capitalize()} not found with ID {user_custom_id}")
