from pydantic import BaseModel, Field

class UserProfileUpdate(BaseModel):
    full_name: str
    gender: str = Field(..., pattern="^(male|female|other)$", description="Must be 'male', 'female', or 'other'")
    language: str
    email: str
    phone: str = Field(..., pattern=r"^0\d{9}$")
    role: str
    joined_date: str
