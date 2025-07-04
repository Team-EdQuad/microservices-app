from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.services.auth_service import authenticate_user, create_access_token
from app.models.admin_model import AdminModel
from app.models import User


router = APIRouter()

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticate the user and return JWT token."""
    user = await authenticate_user(form_data.username, form_data.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create JWT Token
    token = create_access_token(data={"sub": user.email, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}
