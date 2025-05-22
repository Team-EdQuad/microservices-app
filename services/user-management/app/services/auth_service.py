from fastapi import HTTPException,Depends
from fastapi.security import OAuth2PasswordBearer
from bson import ObjectId

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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")  # matches your login endpoint

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
# async def get_current_user(token: str) -> Optional[dict]:
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         user = await db["users"].find_one({"_id": payload["sub"]})
#         if not user:
#             raise HTTPException(status_code=401, detail="Invalid token or user does not exist")
#         return user
#     except jwt.PyJWTError:
#         raise HTTPException(status_code=401, detail="Invalid token")

# async def get_current_user(token: str = Depends(oauth2_scheme)) -> AdminModel:
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         user_id = payload.get("sub")
#         role = payload.get("role")
#         if user_id is None or role is None:
#             raise HTTPException(status_code=401, detail="Invalid token payload")

#         # Fetch user from the correct collection depending on role
#         if role == "admin":
#             user = await db["admins"].find_one({"_id": user_id})
#         elif role == "student":
#             user = await db["students"].find_one({"_id": user_id})
#         elif role == "teacher":
#             user = await db["teachers"].find_one({"_id": user_id})
#         else:
#             raise HTTPException(status_code=403, detail="Invalid user role")

#         if not user:
#             raise HTTPException(status_code=401, detail="User not found")

#         # Convert to your Pydantic model for typing
#         if role == "admin":
#             return AdminModel(**user)
#         # Similarly, return student or teacher models if you want here
#         return user

#     except jwt.PyJWTError:
#         raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        print("Extracted user_id from token:", user_id)
        role = payload.get("role")
        print("Extracted role from token:", role)

        if user_id is None or role is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        try:
            user_object_id = ObjectId(user_id)
        except:
            raise HTTPException(status_code=400, detail="Invalid user ID format")

        if role == "admin":
            user = await db["admin"].find_one({"_id": user_object_id})
            if not user:
                raise HTTPException(status_code=401, detail="User not found")
            
            user["admin_id"] = str(user["_id"])
            del user["_id"]

            user["role"] = "admin"  # <-- Add this line!

            return AdminModel(**user)

        elif role == "student":
            student_doc = await db["student"].find_one({"_id": user_object_id})
            if not student_doc:
                raise HTTPException(status_code=401, detail="User not found")

            student_data = transform_student_doc_to_model(student_doc)
            return StudentRegistration(**student_data)

        elif role == "teacher":
            user = await db["teacher"].find_one({"_id": user_object_id})
            if not user:
                raise HTTPException(status_code=401, detail="User not found")

            user["teacher_id"] = str(user["_id"])
            del user["_id"]
            user["role"] = "teacher"
            return TeacherModel(**user)

        else:
            raise HTTPException(status_code=403, detail="Invalid user role")

    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def transform_student_doc_to_model(doc: dict) -> dict:
    return {
        "student_id": doc.get("student_id", ""),
        "first_name": doc.get("full_name", "").split()[0] if doc.get("full_name") else "",
        "last_name": " ".join(doc.get("full_name", "").split()[1:]) if doc.get("full_name") else "",
        "email": doc.get("email", ""),
        "password": doc.get("password", ""),
        "gender": doc.get("gender", "").lower(),  # make it lowercase for validation
        # "class_name": doc.get("class_id", "")[-1:] if doc.get("class_id") else "",  # extract class name from class_id like "CLS001"
        # "grade": int(doc.get("class_id", "")[-3:-1]) if doc.get("class_id") else 0,  # or other logic for grade
        "class_id": doc.get("class_id", ""),
        "phone": str(doc.get("phone_no", "")),
        "subject": doc.get("subject_id", []),
        "language": doc.get("language", "English"),  # default or from DB
        "club_id": doc.get("club_id", []),
        "sport_id": doc.get("sport_id", []),
        "role": "student"
    } 
# Function to log in a user with email and password
# async def login_service(email: str, password: str):
#     """Authenticate a user based on email and password."""
#     # Check if user exists in the database (this is simplified - you can check for Admin, Student, Teacher)
#     user = await db["users"].find_one({"email": email})
    
#     if not user:
#         raise HTTPException(status_code=401, detail="Invalid credentials")
    
#     # Verify the password
#     if not verify_password(password, user["password"]):
#         raise HTTPException(status_code=401, detail="Invalid credentials")

#     # Create access token (JWT)
#     access_token = create_access_token(data={"sub": str(user["_id"]), "role": user["role"]})
    
#     return {"access_token": access_token, "token_type": "bearer"}

async def login_service(email: str, password: str):
    # Try to find user in each collection
    for collection_name in ["admins", "students", "teachers"]:
        user = await db[collection_name].find_one({"email": email})
        if user and verify_password(password, user["password"]):
            access_token = create_access_token(data={
                "sub": str(user["_id"]),  # this will now be a valid ObjectId string
                "role": user["role"]
            })
            return {"access_token": access_token, "token_type": "bearer"}

    raise HTTPException(status_code=401, detail="Invalid credentials")


# Function to register an admin
async def register_admin(admin_data: AdminModel):
    # Hash the password before saving to DB
    admin_data.role = "admin"
    admin_data.password = hash_password(admin_data.password)
    result = await db["admins"].insert_one(admin_data.dict())
    return {"message": "Admin registered successfully", "admin_id": str(result.inserted_id)}

# Function to register a student
async def register_student(student_data: StudentRegistration):
    # Hash the password before saving to DB
    student_data.role = "student"
    student_data.password = hash_password(student_data.password)
    result = await db["students"].insert_one(student_data.dict())
    return {"message": "Student registered successfully", "student_id": str(result.inserted_id)}

# Function to register a teacher
async def register_teacher(teacher_data: TeacherModel):
    # Hash the password before saving to DB
    teacher_data.role = "teacher"
    teacher_data.password = hash_password(teacher_data.password)
    result = await db["teachers"].insert_one(teacher_data.dict())
    return {"message": "Teacher registered successfully", "teacher_id": str(result.inserted_id)}
