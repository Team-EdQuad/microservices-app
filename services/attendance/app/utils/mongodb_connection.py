from motor.motor_asyncio import AsyncIOMotorClient
# from dotenv import load_dotenv
# from pathlib import Path
# import os

# env_path = Path(__file__).resolve().parent.parent.parent / '.env'
# load_dotenv(dotenv_path=env_path)

# uri = os.getenv("MONGO_URI")
uri = "mongodb+srv://admin:1234@cluster0.ogyx0.mongodb.net/LMS?retryWrites=true&w=majority&appName=Cluster0"
client = AsyncIOMotorClient(uri)

db = client.LMS


attendance_store = db["attendance_store"] 
# attendance_store = db["attendance_store_test"] 
student = db["student"]
class_attendance_summery = db["class_attendance_summery_test"]
# class_attendance_summery = db["class_attendance_summery"]
student_attendance_summery = db["student_attendance_summery_test"]
# student_attendance_summery = db["student_attendance_summery"]
document_store = db["document_store"]
sports = db["sports"]
clubs = db["clubs"]

calendar_events = db["calendar_events"]