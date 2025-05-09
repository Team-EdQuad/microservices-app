from fastapi import HTTPException
from passlib.context import CryptContext
from app.db.database import db  # MongoDB client
import jwt
from datetime import datetime, timedelta
from app.models.admin_model import AdminModel
from app.models.student_model import StudentRegistration
from app.models.teacher_model import TeacherModel
from typing import Optional

# Set up the password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Secret key for encoding JWT
SECRET_KEY = "mysecretkey"  # Use a secure secret key for production
ALGORITHM = "HS256"

# Function to hash passwords
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Function to verify password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Function to create JWT tokens
def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=1)) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Function to retrieve current user from token
async def get_current_user(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user = await db["users"].find_one({"_id": payload["sub"]})
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token or user does not exist")
        return user
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Function to log in a user with email and password
async def login_service(email: str, password: str):
    """Authenticate a user based on email and password."""
    # Check if user exists in the database (this is simplified - you can check for Admin, Student, Teacher)
    user = await db["users"].find_one({"email": email})
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Verify the password
    if not verify_password(password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create access token (JWT)
    access_token = create_access_token(data={"sub": str(user["_id"]), "role": user["role"]})
    
    return {"access_token": access_token, "token_type": "bearer"}

# Function to register an admin
async def register_admin(admin_data: AdminModel):
    # Hash the password before saving to DB
    admin_data.password = hash_password(admin_data.password)
    result = await db["admins"].insert_one(admin_data.dict())
    return {"message": "Admin registered successfully", "admin_id": str(result.inserted_id)}

# Function to register a student
async def register_student(student_data: StudentRegistration):
    # Hash the password before saving to DB
    student_data.password = hash_password(student_data.password)
    result = await db["students"].insert_one(student_data.dict())
    return {"message": "Student registered successfully", "student_id": str(result.inserted_id)}

# Function to register a teacher
async def register_teacher(teacher_data: TeacherModel):
    # Hash the password before saving to DB
    teacher_data.password = hash_password(teacher_data.password)
    result = await db["teachers"].insert_one(teacher_data.dict())
    return {"message": "Teacher registered successfully", "teacher_id": str(result.inserted_id)}
