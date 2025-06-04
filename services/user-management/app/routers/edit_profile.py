from fastapi import APIRouter
from app.models.edit_profile_model import UserProfileUpdate
from app.services.edit_profile_service import update_user_profile

router = APIRouter()

@router.put("/edit_profile/{role}/{user_id}")
async def edit_profile(role: str, user_id: str, profile_update: UserProfileUpdate):
    updated_user = await update_user_profile(role, user_id, profile_update)
    return {"message": "Profile updated successfully", "user": updated_user}

# @router.get("/")
# async def root():
#     return {"message": "Edit user profile"}
