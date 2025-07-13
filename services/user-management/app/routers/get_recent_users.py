from fastapi import APIRouter, Depends, Query, HTTPException
from app.db.database import db # Assuming db is your MongoDB client instance
from bson import ObjectId
from typing import List, Dict

router = APIRouter()

@router.get("/recent-users/{role}")
async def get_recent_users_by_role(role: str, limit: int = 5) -> List[Dict]:
    """
    Fetches the most recent users for a given role.
    Assumes documents have a 'created_at' field for sorting, or can be sorted by '_id' for recency.
    Returns a list of dictionaries with 'id' (custom ID) and 'name' (full_name).
    """
    role_lower = role.lower()
    
    if role_lower not in ["student", "teacher", "admin"]:
        raise ValueError(f"Invalid role provided: '{role}'. Must be 'student', 'teacher', or 'admin'.")

    # In a real application, you would query with ORDER BY created_at DESC LIMIT 5.
    # For MongoDB, sorting by '_id' (which includes a timestamp component) can approximate creation order.
    users_cursor = db[role_lower].find().sort("_id", -1).limit(limit)
    
    recent_users = []
    async for user_doc in users_cursor:
        # Determine the specific ID field name for the role (e.g., student_id, teacher_id)
        user_id_field = {
            "student": "student_id",
            "teacher": "teacher_id",
            "admin": "admin_id",
        }.get(role_lower) 

        user_name_field = "full_name" # Assuming this field exists for all user types

        recent_users.append({
            "id": str(user_doc.get(user_id_field, str(user_doc.get("_id")))), # Use custom ID or MongoDB _id as fallback
            "name": user_doc.get(user_name_field, "N/A"), # Use full_name or "N/A" if not found
            "role": role_lower, # Include role for clarity, though not strictly needed by frontend table
            "phone": user_doc.get("phone_no") or user_doc.get("phone", "N/A"),
            "role": role_lower,
            "email": user_doc.get("email", "N/A"),
            
        })
    return recent_users