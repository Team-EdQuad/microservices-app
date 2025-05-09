from pydantic import BaseModel,EmailStr
from bson import ObjectId

class AdminModel(BaseModel):
    admin_id: str
    first_name: str
    last_name: str
    email: str
    phone: str
    password: str  # Raw password, will be hashed during creation
    role: str  # Role can be admin, student, teacher, etc.

class AdminCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str

    class Config:
        # Allow MongoDB ObjectId to be parsed as string
        arbitrary_types_allowed = True
