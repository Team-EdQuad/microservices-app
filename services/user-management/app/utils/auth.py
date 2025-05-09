from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.db.database import db
from app.models import User  # Assuming your User model exists in models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = "your-secret-key"  # Replace with your actual secret key
ALGORITHM = "HS256"  # Algorithm used for encoding the JWT token

# Dependency to extract and verify token
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        # Decode the JWT token to extract user information
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")  # The 'sub' field typically contains the user ID (or email)
        role = payload.get("role")  # The 'role' field contains the user's role (admin, student, etc.)
        
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
        user = db["users"].find_one({"user_id": user_id})  # Fetch user from DB using user_id
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        
        return {"user_id": user_id, "role": role}  # Returning user data along with role

    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
