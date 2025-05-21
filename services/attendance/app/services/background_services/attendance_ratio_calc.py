from collections import defaultdict
from app.utils.mongodb_connection import attendance_store

async def attendance_ratio_calc(start_date: str, end_date: str, class_id: str, subject_id: str, weekday: str = None, student_id: str = None):
    try:
        match_conditions = {"date": {"$gte": start_date, "$lte": end_date}, "class_id": class_id, "subject_id": subject_id}
        if weekday:
            match_conditions["weekday"] = weekday

        records = await attendance_store.find(match_conditions).to_list(length=None)

        if not records:
            return {"ratio": None, "status": {}, "weekday_attendance_ratio": {}}

        weekday_ratio_totals = defaultdict(float)
        weekday_counts = defaultdict(int)
        student_status_map = {}
        student_total = 0
        student_present = 0

        for record in records:
            status_dict = record.get("status", {})
            record_weekday = record.get("weekday")

            if student_id:
                std_status = status_dict.get(student_id)
                if std_status:
                    if std_status == "present":
                        student_present += 1
                    student_total += 1

                    # Save student's status for that date
                    student_status_map[record["date"]] = std_status

                    # Weekday-wise tracking
                    weekday_ratio_totals[record_weekday] += 1 if std_status == "present" else 0
                    weekday_counts[record_weekday] += 1
            else:
                total_students = len(status_dict)
                present_students = sum(1 for status in status_dict.values() if status == "present")

                if total_students > 0:
                    ratio = present_students / total_students
                    weekday_ratio_totals[record_weekday] += ratio
                    weekday_counts[record_weekday] += 1

                # Save all student statuses
                # student_status_map[record["date"]] = status_dict
                student_status_map = dict(status_dict)


        # Return student-specific results
        if student_id:
            overall_ratio = round(student_present / student_total, 2) if student_total else 0
            overall_ratio = round(
                sum(weekday_ratio_totals.values()) / sum(weekday_counts.values()), 2
            ) if weekday_counts else 0


            return {
                "ratio": overall_ratio,
                "status": student_status_map,
            }

        # Return full class results
        overall_ratio = round(
            sum(weekday_ratio_totals.values()) / sum(weekday_counts.values()), 2
        ) if weekday_counts else 0

        return {
            "ratio": overall_ratio,
            "status": student_status_map,
        }

    except Exception as e:
        print("ERROR inside calculate_attendance:", str(e))
        return {"ratio": 0, "status": {}, "weekday_attendance_ratio": {}}
