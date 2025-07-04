from fastapi import APIRouter, Request, Depends
from datetime import datetime
import pytz
from app.db.database import get_database
router = APIRouter()
from fastapi import Form

@router.post("/logout")
async def logout(req: Request, user_id: str = Form(...), role: str = Form(...)):
    db = get_database()
    collection = db[f"{role}_login_details"]

    timezone = pytz.timezone('Asia/Colombo')
    logout_time = datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S')

    # Find the most recent login event for this user with unknown logout_type
    latest_login = await collection.find_one(
        {f"{role}_id": user_id, "logout_type": "unknown"},
        sort=[("loginTime", -1)]
    )

    if not latest_login:
        return {"message": "No active login session found to update."}

    # Update that document with logoutTime
    result = await collection.update_one(
        {"_id": latest_login["_id"]},
        {"$set": {"logoutTime": logout_time, "logout_type": "manual"}}
    )

    return {"message": "Logout time recorded."}