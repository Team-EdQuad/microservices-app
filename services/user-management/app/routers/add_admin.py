from fastapi import APIRouter, Depends, HTTPException
from app.models.admin_model import AdminCreate
from app.services.auth_service import get_current_user
from app.db.database import db  # Assuming MongoDB is used
from app.models.admin_model import AdminModel
from bson import ObjectId

router = APIRouter()

# @router.post("/add-admin")
# async def add_admin(admin: AdminCreate, current_user: AdminModel = Depends(get_current_user)):
#     """Add a new admin. Only admins can add admins."""
#     if current_user.role != "admin":
#         raise HTTPException(status_code=403, detail="Only admins can add new admins")
    
#     # Insert the new admin into the database (ensure hashing for password in a real scenario)
#     new_admin = admin.dict()
#     await db["admins"].insert_one(new_admin)  # Ensure this operation inserts the data into MongoDB
#     return {"message": "Admin added successfully", "data": new_admin}
@router.post("/add-admin")
async def add_admin(admin: AdminCreate, current_user: AdminModel = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can add new admins")

    new_admin = admin.dict()
    result = await db["admin"].insert_one(new_admin)  # Insert and get InsertOneResult
    
    # Add the inserted _id as string to the returned data
    new_admin["_id"] = str(result.inserted_id)

    return {"message": "Admin added successfully", "data": new_admin}
