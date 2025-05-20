from datetime import datetime
from datetime import timedelta
from app.utils.mongodb_connection import class_attendance_summery, student_attendance_summery
from .update_monthly_attendance import update_monthly_attendance
from .update_yearly_attendance import update_yearly_attendance

async def attendance_summary_process(class_id: str, subject_id: str, date: str = None, student_id: str = None):

    target_date = datetime.strptime(date, "%Y-%m-%d") if date else datetime.now()
    today = datetime.now()
    # today = datetime.strptime("2025-04-20 15:45:32.123456", "%Y-%m-%d %H:%M:%S.%f")

    # Get first day of the month of the target date
    start_date = datetime(target_date.year, target_date.month, 1)

    # Determine end_date based on whether the target date is in the current month
    if target_date.year == today.year and target_date.month == today.month:
        end_date = today
    else:
        # Get the first day of the next month
        next_month = (start_date.replace(day=28) + timedelta(days=4)).replace(day=1)
        # Subtract one day to get the last day of target month
        end_date = next_month - timedelta(days=1)

    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    if not student_id:
         # Fetch attendance document for the given class_id
        class_summary = await class_attendance_summery.find_one({"class_id": class_id})
        
        if not class_summary:
            # Create a new class document if not found
            class_summary = {
                "year": target_date.year, 
                "class_id": class_id, 
                "attendance": []  # Empty attendance initially
            }
            await class_attendance_summery.insert_one(class_summary)  # Save the new class document

        # Find or create subject record
        subject_record = next((record for record in class_summary["attendance"] if record["subject_id"] == subject_id), None)
        if not subject_record:
            subject_record = {
                "subject_id": subject_id,
                "current_month": {},
                "current_year": {},
                "previous_months": []
            }
            class_summary["attendance"].append(subject_record)

        # After modifying class_summary, update it in the database
        await class_attendance_summery.update_one(
            {"class_id": class_id}, 
            {"$set": {"attendance": class_summary["attendance"]}}
        )

        # Now you can safely call `update_monthly_attendance`
        await update_monthly_attendance(class_id, subject_id, start_date_str, end_date_str)

        # call update_yearly_attendance
        await update_yearly_attendance(subject_id, class_id = class_id)

    else:
         # Fetch attendance document for the given student_id
        # student_summary = await class_attendance_summery.find_one({"student_id": student_id})
        student_summary = await student_attendance_summery.find_one({"student_id": student_id})
        
        if not student_summary:
            # Create a new class document if not found
            student_summary = {
                "year": target_date.year, 
                "student_id": student_id,
                "class_id": class_id, 
                "attendance": []  # Empty attendance initially
            }
            await student_attendance_summery.insert_one(student_summary)  # Save the new class document

        # Find or create subject record
        subject_record = next((record for record in student_summary["attendance"] if record["subject_id"] == subject_id), None)
        if not subject_record:
            subject_record = {
                "subject_id": subject_id,
                "current_month": {},
                "current_year": {},
                "previous_months": []
            }
            student_summary["attendance"].append(subject_record)

        # After modifying class_summary, update it in the database
        await student_attendance_summery.update_one(
            {"student_id": student_id}, 
            {"$set": {"attendance": student_summary["attendance"]}}
        )

        # Now you can safely call `update_monthly_attendance`
        await update_monthly_attendance(class_id, subject_id, start_date_str, end_date_str, student_id =student_id)

        # call update_yearly_attendance
        # await update_yearly_attendance(class_id, subject_id)
        await update_yearly_attendance(subject_id, student_id = student_id)
    