from fastapi import HTTPException
from app.db.database import db
from app.utils.validation import validate_phone_number, validate_email  # Corrected import
from app.models.admin_model import AdminCreate
from fastapi.encoders import jsonable_encoder

# Add the missing function to fetch admin by email
async def get_user_by_email(email: str):
    collection = db["admin"]
    admin = await collection.find_one({"email": email})
    return admin

async def add_admin_service(admin_data: AdminCreate):
    if not validate_phone_number(admin_data.phone):
        raise HTTPException(status_code=400, detail="Invalid phone number format. Must start with 0 and contain exactly 10 digits.")

    # Check for existing email or phone in all collections
    collections_to_check = ["admin", "student", "teacher"]

    for collection_name in collections_to_check:
        collection = db[collection_name]
        existing_email = await collection.find_one({"email": admin_data.email})
        if existing_email:
            raise HTTPException(status_code=400, detail=f"Email already exists in {collection_name} collection.")
        
        existing_phone = await collection.find_one({"phone": admin_data.phone})
        if existing_phone:
            raise HTTPException(status_code=400, detail=f"Phone number already exists in {collection_name} collection.")

    # Prepare data to insert
    admin_doc = {
        "admin_id": admin_data.admin_id,
        "first_name": admin_data.first_name,
        "last_name": admin_data.last_name,
        "email": admin_data.email,
        "phone": admin_data.phone,
    }

    result = await db["admin"].insert_one(admin_doc)

    if result.inserted_id:
        admin_doc["_id"] = str(result.inserted_id)
        return jsonable_encoder({"message": "Admin added successfully", "admin": admin_doc})
    else:
        raise HTTPException(status_code=500, detail="Failed to add admin")
async def delete_user_by_credentials(request):
    username = request.username
    password = request.password

    # Verify user credentials
    user = None
    role = None
    for r in ["student", "teacher", "admin"]:
        found = await db[r].find_one({"email": username})
        if found and found.get("password") == password:
            user = found
            role = r
            break

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials.")

    user_id = user["_id"]

    # Delete from main collection
    await db[role].delete_one({"_id": user_id})

    # Delete from login records
    await db[f"{role}_login_details"].delete_many({"email": user["email"]})

    return {"message": f"User {user['email']} and all related data deleted successfully"}