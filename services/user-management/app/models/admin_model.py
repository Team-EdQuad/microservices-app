from pydantic import BaseModel,EmailStr, Field
from bson import ObjectId
from datetime import datetime
from typing import Optional, Union
from datetime import date

class AdminModel(BaseModel):
    admin_id: str
    first_name: str
    last_name: str
    full_name: str
    email: str
    phone: str
    password: str  # Raw password, will be hashed during creation
    role: str  # Role can be admin, student, teacher, etc.
    join_date: Optional[Union[date, datetime]] = None
    last_edit_date: Optional[Union[date, datetime]] = None
    gender: str

# class AdminCreate(BaseModel):
#     admin_id: str = Field(..., pattern=r"^ADM\d{3}$")
#     first_name: str
#     last_name: str
#     email: EmailStr
#     password: str
#     phone: str = Field(..., pattern=r"^\d{10}$")
#     role: str = "admin"
#     full_name: str
#     join_date: date
#     last_edit_date: date
#     gender: str = Field(..., pattern="^(male|female)$")



#     class Config:
#         # Allow MongoDB ObjectId to be parsed as string
#         arbitrary_types_allowed = True


class AdminCreate(BaseModel):
    admin_id: str = Field(..., pattern=r"^ADM\d{3}$")
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    phone: str = Field(..., pattern=r"^\d{10}$")
    role: str = "admin"
    full_name: Optional[str] = None
    join_date: Optional[Union[date, datetime]] = None
    last_edit_date: Optional[Union[date, datetime]] = None
    gender: str = Field(..., pattern="^(male|female)$")

    class Config:
        arbitrary_types_allowed = True
