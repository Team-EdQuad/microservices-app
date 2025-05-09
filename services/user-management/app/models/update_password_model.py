# app/models/update_password_model.py

from pydantic import BaseModel

class UpdatePasswordRequest(BaseModel):
    email: str
    password: str
