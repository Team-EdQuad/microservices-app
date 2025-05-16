from app.utils.mongodb_connection import student_attendance_summery, class_attendance_summery
from collections import defaultdict

async def update_yearly_attendance(subject_id: str, class_id: str = None, student_id: str = None):
    try:
        if student_id:
            summary_doc = await student_attendance_summery.find_one({"student_id": student_id})
        else:
            summary_doc = await class_attendance_summery.find_one({"class_id": class_id})

        if not summary_doc or "attendance" not in summary_doc:
            print("No attendance data found.")
            return

        subject_record = next((item for item in summary_doc["attendance"] if item["subject_id"] == subject_id), None)
        if not subject_record:
            print("Subject record not found.")
            return

        total_months = 0
        total_month_ratio = 0.0
        total_weekday_ratios = defaultdict(float)
        total_weekday_days = defaultdict(int)

        # Current month
        current = subject_record.get("current_month", {})
        if "monthly_attendance_ratio" in current:
            total_months += 1
            total_month_ratio += current["monthly_attendance_ratio"]

        if "weekday_attendance_ratio" in current:
            for weekday, ratio in current["weekday_attendance_ratio"].items():
                total_weekday_ratios[weekday] += ratio
                total_weekday_days[weekday] += 1

        # Previous months
        for month_data in subject_record.get("previous_months", []):
            if "monthly_attendance_ratio" in month_data:
                total_months += 1
                total_month_ratio += month_data["monthly_attendance_ratio"]
            if "weekday_attendance_ratio" in month_data:
                for weekday, ratio in month_data["weekday_attendance_ratio"].items():
                    total_weekday_ratios[weekday] += ratio
                    total_weekday_days[weekday] += 1

        yearly_ratio = total_month_ratio / total_months if total_months > 0 else 0
        
        weekly_ratios = {}
        for weekday, ratio_sum in total_weekday_ratios.items():
            days = total_weekday_days.get(weekday)
            if days is not None and days > 0:
                weekly_ratios[weekday] = ratio_sum / days
            else:
                weekly_ratios[weekday] = None 


        subject_record.setdefault("current_year", {})
        subject_record["current_year"]["yearly_attendance_ratio"] = yearly_ratio
        if weekly_ratios:
            subject_record["current_year"]["weekday_attendance_ratio"] = weekly_ratios

        filter_query = {"student_id": student_id, "attendance.subject_id": subject_id} if student_id else {"class_id": class_id, "attendance.subject_id": subject_id}
        update_query = {"$set": {"attendance.$.current_year": subject_record["current_year"]}}

        if student_id:
            await student_attendance_summery.update_one(filter_query, update_query)
        else:
            await class_attendance_summery.update_one(filter_query, update_query)

    except Exception as e:
        print(f"Error in make_attendance_summary_for_year: {e}")
