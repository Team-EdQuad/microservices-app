from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException
from app.db.database import db
from app.models.edit_profile_model import UserProfileUpdate

user_collection = db.users

async def update_user_profile(email: str, profile_update: UserProfileUpdate):
    user = await user_collection.find_one({"email": email})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = {
        "full_name": profile_update.full_name,
        "gender": profile_update.gender,
        "language": profile_update.language,
        "email": profile_update.email,
        "phone": profile_update.phone,
        "role": profile_update.role,
        "joined_date": profile_update.joined_date,
        "last_edited_date": datetime.utcnow().isoformat(),
        "last_edited_phone_date": datetime.utcnow().isoformat()
    }

    await user_collection.update_one({"_id": ObjectId(user["_id"])}, {"$set": update_data})
    return update_data
