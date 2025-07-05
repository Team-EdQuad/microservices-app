from datetime import datetime
from app.anomaly_detection.agents.time_agent import TimeAgent
from app.anomaly_detection.agents.location_agent import LocationAgent
from app.anomaly_detection.agents.device_agent import DeviceAgent
from app.db.database import get_database
from pydantic import BaseModel
from typing import Optional


db = get_database()

time_agent = TimeAgent()
location_agent = LocationAgent()
device_agent = DeviceAgent()


class LoginInput(BaseModel):
    username: str
    role: str
    timestamp: str  # format: "YYYY-MM-DD HH:MM:SS"
    location: Optional[str]
    device_info: Optional[str]

def extract_hour(timestamp_str):
    dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
    return dt.hour

def preprocess_location(location):
    if not location or location.lower().startswith("unknown"):
        return "Unknown"
    return location.split(",")[0].strip()

def preprocess_device(device_info):
    return device_info[:50]  # truncate user agent

def detect_and_mark(collection_name):
    collection = db[collection_name]
    query = {"anomaly_checked": {"$ne": True}}
    records = collection.find(query)

    for record in records:
        username = record.get("username")
        role = record.get("role")
        timestamp = record.get("timestamp")
        location_raw = record.get("location")
        device_raw = record.get("device_info")

        if not (username and role and timestamp and location_raw and device_raw):
            collection.update_one({"_id": record["_id"]}, {"$set": {"anomaly_checked": True}})
            continue

        hour = extract_hour(timestamp)
        location = preprocess_location(location_raw)
        device = preprocess_device(device_raw)

        is_time_anomaly = time_agent.detect(hour)
        is_location_anomaly = location_agent.detect(location)
        is_device_anomaly = device_agent.detect(device)

        is_overall_anomaly = is_time_anomaly or is_location_anomaly or is_device_anomaly

        db["login_anomaly_results"].insert_one({
            "username": username,
            "role": role,
            "hour": hour,
            "location": location,
            "device": device,
            "is_time_anomaly": is_time_anomaly,
            "is_location_anomaly": is_location_anomaly,
            "is_device_anomaly": is_device_anomaly,
            "is_overall_anomaly": is_overall_anomaly,
            "source_collection": collection_name,
            "timestamp": timestamp
        })

        collection.update_one({"_id": record["_id"]}, {"$set": {"anomaly_checked": True}})

    print(f"Processed {collection_name} records.")

def detect_login_anomaly_logic(data: LoginInput, db_client):
    hour = extract_hour(data.timestamp)
    location = preprocess_location(data.location)
    device = preprocess_device(data.device_info)

    # is_time_anomaly = time_agent.detect(hour)
    # is_location_anomaly = location_agent.detect(location)
    # is_device_anomaly = device_agent.detect(device)

    is_time_anomaly = bool(time_agent.detect(hour))
    is_location_anomaly = bool(location_agent.detect(location))
    is_device_anomaly = bool(device_agent.detect(device))

    is_overall_anomaly = is_time_anomaly or is_location_anomaly or is_device_anomaly

    # Save the result to the database
    db_client["login_anomaly_results"].insert_one({
        "username": data.username,
        "role": data.role,
        "hour": hour,
        "location": location,
        "device": device,
        "is_time_anomaly": is_time_anomaly,
        "is_location_anomaly": is_location_anomaly,
        "is_device_anomaly": is_device_anomaly,
        "is_overall_anomaly": is_overall_anomaly,
        "timestamp": data.timestamp
    })

    return {
        "is_time_anomaly": is_time_anomaly,
        "is_location_anomaly": is_location_anomaly,
        "is_device_anomaly": is_device_anomaly,
        "is_overall_anomaly": is_overall_anomaly
    }

def retrain_models(db_client):
    print("Retraining models... (not implemented)")
    # Implement retraining logic here if needed


def run_all():
    for col in ["student_login_details", "teacher_login_details", "admin_login_details"]:
        detect_and_mark(col)

if __name__ == "__main__":
    run_all()



