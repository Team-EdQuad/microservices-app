from fastapi import APIRouter, Depends, HTTPException
from app.models.admin_model import AdminCreate
from app.services.auth_service import get_current_user
from app.db.database import db  # Assuming MongoDB is used
from app.models.admin_model import AdminModel
from bson import ObjectId
from datetime import datetime, date
import pytz

ist = pytz.timezone('Asia/Kolkata')
now_ist = datetime.now(ist)  # Current time in IST with timezone info

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
# @router.post("/add-admin")
# async def add_admin(admin: AdminCreate, current_user: AdminModel = Depends(get_current_user)):
#     if current_user.role != "admin":
#         raise HTTPException(status_code=403, detail="Only admins can add new admins")

#     new_admin = admin.dict()
#     result = await db["admin"].insert_one(new_admin)  # Insert and get InsertOneResult
    
#     # Add the inserted _id as string to the returned data
#     new_admin["_id"] = str(result.inserted_id)

#     return {"message": "Admin added successfully", "data": new_admin}
# In your User Management Service (8001)

def date_to_datetime_with_ist(d=None):
    if d is None:
        return datetime.now(ist)
    if isinstance(d, datetime):
        return d.astimezone(ist)
    if isinstance(d, date):
        return datetime(d.year, d.month, d.day, tzinfo=ist)
    return d



# @router.post("/add-admin")
# async def add_admin(admin: AdminCreate, current_user: AdminModel = Depends(get_current_user)):
#     try:
#         print(f"Current user: {current_user}")
#         print(f"Current user role: {getattr(current_user, 'role', 'No role attribute')}")
        
        
#         # Check if current_user has role attribute and is admin
#         if not hasattr(current_user, 'role') or current_user.role != "admin":
#             raise HTTPException(status_code=403, detail="Only admins can add new admins")

#         # Convert admin data to dict
#         new_admin = admin.dict()
#         print(f"Admin data to insert: {new_admin}")
#         # Set join_date and last_edit_date to now if not provided
#         now = datetime.now()
#         new_admin["join_date"] = new_admin.get("join_date") or now
#         new_admin["last_edit_date"] = new_admin.get("last_edit_date") or now
#         # Set full_name as first_name + last_name
#         new_admin["full_name"] = f"{new_admin['first_name']} {new_admin['last_name']}"
#         # Insert into DB
        
        
#         # Check if admin with same email already exists
#         existing_admin = await db["admin"].find_one({"email": new_admin.get("email")})
#         if existing_admin:
#             raise HTTPException(status_code=400, detail="Admin with this email already exists")
        
#         # Insert the new admin
#         result = await db["admin"].insert_one(new_admin)
        
#         # if not result.inserted_id:
#         #     raise HTTPException(status_code=500, detail="Failed to insert admin")
        
#         # Add the inserted _id as string to the returned data
#         # new_admin["_id"] = str(result.inserted_id)
#         return {"message": "Admin created", "admin_id": str(result.inserted_id)}

#         # return {"message": "Admin added successfully", "data": new_admin}
        
#     except HTTPException:
#         # Re-raise HTTP exceptions as-is
#         raise
#     except Exception as e:
#         print(f"Error in add_admin: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/add-admin")
async def add_admin(admin: AdminCreate, current_user: AdminModel = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can add new admins")

    new_admin = admin.dict()
    now = datetime.now()
    # new_admin["join_date"] = date_to_datetime(new_admin.get("join_date") or now)
    # new_admin["last_edit_date"] = date_to_datetime(new_admin.get("last_edit_date") or now)
    new_admin["join_date"] = date_to_datetime_with_ist(new_admin.get("join_date"))
    new_admin["last_edit_date"] = date_to_datetime_with_ist(new_admin.get("last_edit_date"))
    new_admin["full_name"] = f"{new_admin['first_name']} {new_admin['last_name']}"

    existing_admin = await db["admin"].find_one({"email": new_admin.get("email")})
    if existing_admin:
        raise HTTPException(status_code=400, detail="Admin with this email already exists")

    result = await db["admin"].insert_one(new_admin)
    return {"message": "Admin created", "admin_id": str(result.inserted_id)}