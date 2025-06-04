from fastapi import APIRouter, HTTPException, Request, Form
from pydantic import BaseModel
from user_agents import parse
import datetime
import pytz
import httpx

from app.db.database import get_database
from app.services.auth_service import create_access_token

router = APIRouter()

class LoginRequest(BaseModel):
    username: str  # This should be an email
    password: str

# Utility: Get client's IP address
def get_client_ip(req: Request):
    x_forwarded_for = req.headers.get("X-Forwarded-For")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]
    return req.client.host

# Utility: Get location by IP
async def get_location(ip_address: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://ip-api.com/json/{ip_address}")
            if response.status_code == 200:
                data = response.json()
                city = data.get('city', 'Unknown')
                country = data.get('country', 'Unknown')
                region = data.get('regionName', 'Unknown')
                latitude = data.get('lat', 'Unknown')
                longitude = data.get('lon', 'Unknown')
                return f"{city}, {region}, {country} (Lat: {latitude}, Lon: {longitude})"
    except Exception as e:
        print(f"Location Fetch Error: {e}")
    return "Unknown"

# Utility: Detect device type
def get_login_type(user_agent: str):
    ua = parse(user_agent)
    if ua.is_mobile:
        return "mobile"
    elif ua.is_tablet:
        return "tablet"
    elif ua.is_pc:
        return "desktop"
    else:
        return "unknown"

# Check user validity
async def is_valid_user(username: str, password: str):
    db = get_database()
    teacher = await db["teacher"].find_one({"email": username})
    student = await db["student"].find_one({"email": username})
    admin = await db["admin"].find_one({"email": username})

    if teacher and teacher.get("password") == password:
        return teacher, "teacher", "teacher_id"
    if student and student.get("password") == password:
        return student, "student", "student_id"
    if admin and admin.get("password") == password:
        return admin, "admin", "admin_id"

    return None, None, None

# Save login info
async def save_login_details(username: str, user_id: str, role: str, user_key: str, status: str, req: Request, event_type: str):
    db = get_database()
    collection = db[f"{role}_login_details"]

    ip_address = get_client_ip(req)
    user_agent = req.headers.get("user-agent", "Unknown")
    location = await get_location(ip_address)
    login_type = get_login_type(user_agent)

    timezone = pytz.timezone('Asia/Colombo')
    timestamp = datetime.datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S')

    log_entry = {
        user_key: user_id,
        "username": username,
        "role": role,
        "status": status,
        "IP_address": ip_address,
        "location": location,
        "device_info": user_agent,
        "event_type": event_type,
        "login_type": login_type,
        "logout_type": "unknown",
        "timestamp": timestamp
    }
    await collection.insert_one(log_entry)

@router.post("/login")
async def login(req: Request, username: str = Form(...), password: str = Form(...)):
    user, role, user_key = await is_valid_user(username, password)
    if user:
        # Use ObjectId string as 'sub' in the token
        # token = create_access_token(data={"sub": str(user.get("_id")), "role": role})
        # user_id_value = str(user.get("_id")) if role != "student" else user.get("student_id")
        # token = create_access_token(data={"sub": user_id_value, "role": role})
        user_id_value = user.get(f"{role}_id")  # e.g., admin_id, teacher_id, student_id
        token = create_access_token(data={
            "sub": user_id_value,
            "role": role
        })

        
        # Save login details to the database
        await save_login_details(
            username=username,
            user_id=user_id_value,
            role=role,
            user_key=user_key,
            status="success",
            req=req,
            event_type="login"
        )
        
        return {"access_token": token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")
