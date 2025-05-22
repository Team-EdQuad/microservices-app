from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import jwt
from app.db.database import db
from app.models import User  # Assuming your User model exists in models

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login") 

from app.models.admin_model import AdminModel
from app.models.student_model import StudentRegistration
from app.models.teacher_model import TeacherModel
from bson import ObjectId

SECRET_KEY = "your-secret-key"  # Replace with your actual secret key
ALGORITHM = "HS256"  # Algorithm used for encoding the JWT token

# Dependency to extract and verify token
# def get_current_user(token: str = Depends(oauth2_scheme)):
#     try:
#         # Decode the JWT token to extract user information
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         user_id = payload.get("sub")  # The 'sub' field typically contains the user ID (or email)
#         role = payload.get("role")  # The 'role' field contains the user's role (admin, student, etc.)
        
#         if user_id is None:
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
#         user = db["users"].find_one({"user_id": user_id})  # Fetch user from DB using user_id
#         if user is None:
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        
#         return {"user_id": user_id, "role": role}  # Returning user data along with role

#     except JWTError:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        role = payload.get("role")

        if user_id is None or role is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        user_object_id = ObjectId(user_id)

        if role == "admin":
            user = await db["admins"].find_one({"_id": user_object_id})
            if not user:
                raise HTTPException(status_code=401, detail="User not found")
            user["admin_id"] = str(user["_id"])
            del user["_id"]
            user["role"] = "admin"
            return AdminModel(**user)

        elif role == "student":
            student_doc = await db["students"].find_one({"_id": user_object_id})
            if not student_doc:
                raise HTTPException(status_code=401, detail="User not found")
            student_data = transform_student_doc_to_model(student_doc)
            return StudentRegistration(**student_data)

        elif role == "teacher":
            user = await db["teachers"].find_one({"_id": user_object_id})
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