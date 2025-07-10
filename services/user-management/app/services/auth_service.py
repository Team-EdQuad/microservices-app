from fastapi import HTTPException,Depends
from fastapi.security import OAuth2PasswordBearer
from bson import ObjectId

from passlib.context import CryptContext
from app.db.database import db  # MongoDB client
from jose import jwt
from dateutil.parser import parse
from datetime import datetime, timedelta,date
from app.models.admin_model import AdminModel
from app.models.student_model import StudentRegistration
from app.models.teacher_model import TeacherModel
from typing import Optional,Union

# Set up the password hashing context
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Secret key for encoding JWT
SECRET_KEY = "mysecretkey"  # Use a secure secret key for production
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")  # matches your login endpoint

def parse_date(value: Optional[Union[str, datetime, date]]) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, (datetime, date)):
        return value
    try:
        return parse(value)
    except Exception:
        return None
    
    
# Function to hash passwords
def hash_password(password: str) -> str:
    # return pwd_context.hash(password)
    return password

# Function to verify password
# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     return pwd_context.verify(plain_password, hashed_password)
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return plain_password == hashed_password 

# Function to create JWT tokens
def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=1)) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        role = payload.get("role")

        print(f"DEBUG: token payload - user_id: {user_id}, role: {role}")

        if user_id is None or role is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        role = role.lower()
        collection_map = {
            "admin": "admin",
            "teacher": "teacher",
            "student": "student"
        }
        id_field_map = {
            "admin": "admin_id",
            "teacher": "teacher_id",
            "student": "student_id"
        }

        collection_name = collection_map.get(role)
        id_field = id_field_map.get(role)

        if not collection_name or not id_field:
            raise HTTPException(status_code=403, detail="Invalid user role")

        # Query by custom ID field as string, no ObjectId conversion
        user_doc = await db[collection_name].find_one({id_field: user_id})
        print(f"DEBUG: user_doc fetched from DB: {user_doc}")
        if not user_doc:
            raise HTTPException(status_code=404, detail=f"{role.capitalize()} not found")

        # Normalize user_doc for Pydantic model
        user_doc[id_field] = user_id  # Ensure ID field is present
        user_doc["role"] = role
        
        
        if role == "student":
            student_data = transform_student_doc_to_model(user_doc)
            return StudentRegistration(**student_data)

        elif role == "admin":
            join_date_parsed = parse_date(user_doc.get("join_date"))
            last_edit_parsed = parse_date(user_doc.get("last_edit_date"))

            user_doc["join_date"] = join_date_parsed
            user_doc["last_edit_date"] = last_edit_parsed

            return AdminModel(**user_doc)

        elif role == "teacher":
            # Optionally transform teacher_doc if needed (e.g. rename phone_no to phone)
            teacher_data = {
                "teacher_id": user_doc.get("teacher_id"),
                "email": user_doc.get("email"),
                "full_name": user_doc.get("full_name"),
                "first_name": user_doc.get("first_name"),
                "last_name": user_doc.get("last_name"),
                "gender": user_doc.get("gender"),
                "phone_no": user_doc.get("Phone_no"),  # normalize key here
                "join_date": user_doc.get("join_date"),
                "last_edit_date": user_doc.get("last_edit_date"),
                "subjects_classes": user_doc.get("subjects_classes", []),
                "role": "teacher"

            }
            return TeacherModel(**teacher_data)

    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def transform_student_doc_to_model(doc: dict) -> dict:
    def parse_date(date_str):
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date() if isinstance(date_str, str) else date_str.date()
        except Exception:
            return date.today()

    return {
        "student_id": doc.get("student_id", ""),
        "first_name": doc.get("full_name", "").split()[0] if doc.get("full_name") else "",
        "last_name": " ".join(doc.get("full_name", "").split()[1:]) if doc.get("full_name") else "",
        "full_name": doc.get("full_name", ""),
        "email": doc.get("email", ""),
        "password": doc.get("password", ""),
        "gender": doc.get("gender", "").lower(),
        "class_id": doc.get("class_id", ""),
        "phone_no": str(doc.get("phone_no", "")),
        "subject_id": doc.get("subject_id", []),
        "club_id": doc.get("club_id", []),
        "sport_id": doc.get("sport_id", []),
        "join_date": parse_date(doc.get("join_date")),
        "last_edit_date": parse_date(doc.get("last_edit_date")),
        "role": "student"
    }

async def login_service(email: str, password: str):
    for collection_name, role in [("admin", "admin"), ("student", "student"), ("teacher", "teacher")]:
        user = await db[collection_name].find_one({"email": email})
        if user and verify_password(password, user["password"]):
            user_id = user.get(f"{role}_id")  # e.g., admin_id, student_id, teacher_id
            access_token = create_access_token(data={
                "sub": user_id,
                "role": role
            })
            return {"access_token": access_token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

# Function to register an admin
async def register_admin(admin_data: AdminModel):
    # Hash the password before saving to DB
    admin_data.role = "admin"
    admin_data.password = hash_password(admin_data.password)
    result = await db["admin"].insert_one(admin_data.dict())
    return {"message": "Admin registered successfully", "admin_id": str(result.inserted_id)}

# Function to register a student
async def register_student(student_data: StudentRegistration):
    # Hash the password before saving to DB
    student_data.role = "student"
    student_data.password = hash_password(student_data.password)
    result = await db["student"].insert_one(student_data.dict())
    return {"message": "Student registered successfully", "student_id": str(result.inserted_id)}

# Function to register a teacher
async def register_teacher(teacher_data: TeacherModel):
    # Hash the password before saving to DB
    teacher_data.role = "teacher"
    teacher_data.password = hash_password(teacher_data.password)
    result = await db["teacher"].insert_one(teacher_data.dict())
    return {"message": "Teacher registered successfully", "teacher_id": str(result.inserted_id)}
