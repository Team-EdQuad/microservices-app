from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from .update_monthly_attendance import update_monthly_attendance
from app.utils.mongodb_connection import class_attendance_summery, student_attendance_summery
from datetime import datetime

scheduler = AsyncIOScheduler()

async def schedule_update_monthly_attendance():
    print("scheduled job running")
    # today = datetime.strptime("2025-04-30 15:45:32.123456", "%Y-%m-%d %H:%M:%S.%f")
    today = datetime.now()
    start_date = today.replace(day=1).strftime("%Y-%m-%d")
    end_date = today.strftime("%Y-%m-%d")

    async for class_doc in class_attendance_summery.find({}):
        class_id = class_doc["class_id"]
        for subject in class_doc.get("attendance", []):
            subject_id = subject.get("subject_id")
            if subject_id:
                try:
                    await update_monthly_attendance(
                        class_id, subject_id, start_date, end_date, is_scheduled=True
                    )
                except Exception as e:
                    print(f"Error updating {class_id} - {subject_id}: {e}")

    async for student_doc in student_attendance_summery.find({}):
        student_id = student_doc["student_id"]
        class_id = student_doc["class_id"]
        for subject in student_doc.get("attendance", []):
            subject_id = subject.get("subject_id")
            if subject_id:
                try:
                    await update_monthly_attendance(
                        class_id, subject_id, start_date, end_date, is_scheduled=True, student_id=student_id
                    )

                except Exception as e:
                    print(f"Error updating {student_id} - {subject_id}: {e}")

# Function to set up the scheduler
def setup_scheduler():
    scheduler.add_job(
        schedule_update_monthly_attendance, 
        # CronTrigger(hour=22, minute=52, day='*', month='*', week='*', day_of_week='*'),
        CronTrigger(hour=23, minute=59, day='28-31', month='*', week='*', day_of_week='*'),
        id="monthly_attendance_update",
        max_instances=1,
        replace_existing=True
    )

# Function to start the scheduler
def start_scheduler():
    scheduler.start()