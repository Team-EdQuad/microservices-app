from fastapi import HTTPException
from app.db.database import db
from bson import ObjectId

async def delete_user_account(username: str, password: str):
    # Check each role collection for the user
    for role in ["student", "teacher", "admin"]:
        user = await db[role].find_one({"email": username})
        if user and user.get("password") == password:
            user_id_obj = user["_id"]

            # Delete from user collection
            await db[role].delete_one({"_id": user_id_obj})

            # Delete related login details
            await db[f"{role}_login_details"].delete_many({"email": user["email"]})

            return f"User {user['email']} and all related data deleted successfully"

    raise HTTPException(status_code=404, detail="User not found or invalid credentials.")
