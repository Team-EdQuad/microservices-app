
from datetime import datetime, timedelta
from app.utils.mongodb_connection import class_attendance_summery, student_attendance_summery
from .attendance_ratio_calc import attendance_ratio_calc

async def update_monthly_attendance(class_id: str, subject_id: str, start_date: str, end_date: str, is_scheduled: bool = False, student_id: str = None):
    """
    Generates and stores attendance summary (daily, monthly, weekday-wise) for a class or individual student.
    """
    try:
        print("is_scheduled", is_scheduled)
        # Convert input dates
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")

        attendance_summary = {
            "month": start_dt.strftime("%B"),
            "daily_attendance": {},
            "monthly_attendance_ratio": 0.0,
            "weekday_attendance_ratio": {}
        }

        # Daily attendance loop
        current_date = start_dt
        while current_date <= end_dt:
            day_str = current_date.strftime("%Y-%m-%d")
            weekday = current_date.strftime("%A")

            daily_attendance = await attendance_ratio_calc(day_str, day_str, class_id, subject_id, student_id=student_id)

            if student_id:
                if daily_attendance is not None:
                    if daily_attendance and isinstance(daily_attendance, str):
                        attendance_summary["daily_attendance"][day_str] = daily_attendance
                    elif isinstance(daily_attendance, dict) and "status" in daily_attendance:
                        status = daily_attendance["status"].get(day_str)
                        if status:
                            attendance_summary["daily_attendance"][day_str] = status

            else:
                ratio = daily_attendance.get("ratio")
                if daily_attendance and ratio is not None and ratio > 0 and daily_attendance.get("status"):

                    attendance_summary["daily_attendance"][day_str] = {
                        "ratio": daily_attendance["ratio"],
                        "status": daily_attendance["status"]
                    }

            current_date += timedelta(days=1)

        # Monthly attendance
        monthly_attendance = await attendance_ratio_calc(start_date, end_date, class_id, subject_id, student_id=student_id)
        attendance_summary["monthly_attendance_ratio"] = monthly_attendance.get("ratio", 0.0) if monthly_attendance else 0.0

        # Weekday-wise attendance
        for weekday in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
            weekday_data = await attendance_ratio_calc(start_date, end_date, class_id, subject_id, weekday=weekday, student_id=student_id)
            if weekday_data and "ratio" in weekday_data:
                attendance_summary["weekday_attendance_ratio"][weekday] = weekday_data["ratio"]


        # Store result
        if not student_id:

            # Fetch or prepare the main attendance document
            doc = await class_attendance_summery.find_one({"class_id": class_id})
            if not doc:
                doc = {"class_id": class_id, "attendance": []}

            attendance_list = doc.setdefault("attendance", [])
            subject_record = next((item for item in attendance_list if item["subject_id"] == subject_id), None)

            if not subject_record:
                subject_record = {"subject_id": subject_id}
                attendance_list.append(subject_record)

            today = datetime.now()
            

            if is_scheduled and start_dt.month != today.month:
                print("Iam in scheduled")
                # print(attendance_summary)
                prev_months = subject_record.setdefault("previous_months", [])
                existing_month = next((m for m in prev_months if m["month"] == attendance_summary["month"]), None)
                # print("existing_month", existing_month)
                if existing_month:
                    existing_month.update(attendance_summary)
                else:
                    prev_months.append(attendance_summary)
                # print(prev_months)
            else:
                subject_record["current_month"] = subject_record.get("current_month", {})
                subject_record["current_month"].update(attendance_summary)


            await class_attendance_summery.update_one(
                {"class_id": class_id},
                {"$set": {"attendance": attendance_list}},
                upsert=True
            )

        else:

            # Fetch or prepare the main attendance document
            doc = await student_attendance_summery.find_one({"student_id": student_id})
            if not doc:
                doc = {"student_id": student_id, "attendance": []}

            student_attendance_list = doc.setdefault("attendance", [])
            subject_record = next((item for item in student_attendance_list if item["subject_id"] == subject_id), None)

            if not subject_record:
                subject_record = {"subject_id": subject_id}
                student_attendance_list.append(subject_record)

            today = datetime.now()
            

            if is_scheduled and start_dt.month != today.month:
                prev_months = subject_record.setdefault("previous_months", [])
                existing_month = next((m for m in prev_months if m["month"] == attendance_summary["month"]), None)
                if existing_month:
                    existing_month.update(attendance_summary)
                else:
                    prev_months.append(attendance_summary)
            else:
                subject_record["current_month"] = subject_record.get("current_month", {})
                subject_record["current_month"].update(attendance_summary)


            await student_attendance_summery.update_one(
                {"student_id": student_id},
                {"$set": {"attendance": student_attendance_list}},
                upsert=True
            )

    except Exception as e:
        print(f"[make_attendance_summary_for_month] Error: {str(e)}")
        raise
