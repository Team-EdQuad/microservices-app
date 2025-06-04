from fastapi import APIRouter, HTTPException
from app.models.update_password_model import UpdatePasswordRequest
from app.services.update_password_service import update_user_password
import re

router = APIRouter()

@router.put("/update_password")
async def update_password(request: UpdatePasswordRequest):
    # Validate email format
    if not re.match(r"[^@]+@[^@]+\.[^@]+", request.email):
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    return await update_user_password(request)

# @router.get("/")
# async def root():
#     return {"message": "Forgot Password"}
