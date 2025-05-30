from fastapi import APIRouter, HTTPException

from .database import student_table, subject_table, content_table, student_content_table
from .database import assignment_table, submission_table, academic_attendance_table
from .database import exam_table, behavioural_table
# from .ml_model_loader import model

from datetime import datetime, timedelta
from collections import defaultdict
# import pandas as pd
# import pytz

model_features_router = APIRouter()

@model_features_router.get("/{student_id}/{class_id}/model-features")
async def get_model_features(student_id: str, class_id: str):
    try:
        student = student_table.find_one({"student_id": student_id, "class_id": class_id})
        if not student:
            raise HTTPException(status_code=404, detail="Student not found in given class")

        subject_ids = student.get("subject_id", [])
        if not subject_ids or len(subject_ids) < 3:
            raise HTTPException(status_code=400, detail="At least 6 subjects are expected for modeling")

        ### ---- LMS Completion ----
        lms_completion = {}
        for i, subject_id in enumerate(subject_ids[:3]):
            total_contents = content_table.count_documents({"subject_id": subject_id, "class_id": class_id})
            completed_contents = student_content_table.count_documents({
                "subject_id": subject_id, "class_id": class_id,
                "student_id": student_id, "status": "Active"
            })
            percent = (completed_contents / total_contents) * 100 if total_contents else 0
            lms_completion[f"lms_sub{i+1}"] = round(percent, 2)

        ### ---- Exam Marks ----
        exam_marks = exam_table.find_one({"student_id": student_id, "class_id": class_id})
        exam_averages = {f"exam_sub{i+1}": 0 for i in range(6)}
        if exam_marks:
            for i, subject in enumerate(exam_marks.get("exam_marks", [])[:6]):
                all_marks = [exam["marks"] for exam in subject["exams"] if "marks" in exam]
                avg = sum(all_marks) / len(all_marks) if all_marks else 0
                exam_averages[f"exam_sub{i+1}"] = round(avg, 2)

        ### ---- Assignment Marks & Late Submission ----
        assi_marks = {f"assi_sub{i+1}": 0 for i in range(6)}
        late_count = 0
        total_assignments = 0

        for i, subject_id in enumerate(subject_ids[:6]):
            assignments = list(assignment_table.find({"subject_id": subject_id, "class_id": class_id}))
            submissions = list(submission_table.find({
                "student_id": student_id, "subject_id": subject_id, "class_id": class_id
            }))
            sub_map = {s["assignment_id"]: s for s in submissions}

            marks_total = 0
            marks_count = 0

            for a in assignments:
                total_assignments += 1
                aid = a["assignment_id"]
                deadline = datetime.fromisoformat(a["deadline"]) if isinstance(a["deadline"], str) else a["deadline"]

                if aid in sub_map:
                    submission = sub_map[aid]
                    if submission.get("marks") is not None:
                        marks_total += submission["marks"]
                        marks_count += 1

                    # Check late submission
                    sub_time = datetime.fromisoformat(submission["submit_time_date"]) if isinstance(submission["submit_time_date"], str) else submission["submit_time_date"]
                    if deadline and sub_time > deadline:
                        late_count += 1

            avg = (marks_total / marks_count) if marks_count else 0
            assi_marks[f"assi_sub{i+1}"] = round(avg, 2)

        assi_late_pct = round((late_count / total_assignments) * 100, 2) if total_assignments else 0

        ### ---- Academic Attendance ----
        attendance_records = academic_attendance_table.find({"class_id": class_id})
        total_days, present_days = 0, 0
        for rec in attendance_records:
            if rec.get("subject_id") == "academic":
                total_days += 1
                if student_id in rec["status"] and rec["status"][student_id] == "present":
                    present_days += 1

        academic_attendance_rate = round((present_days / total_days) * 100, 2) if total_days else 0

        ### ---- Non-Academic Attendance ----
        activities = student.get("sport_id", []) + student.get("club_id", [])
        non_academic_records = academic_attendance_table.find({
            "class_id": class_id,
            "subject_id": {"$in": activities},
        })

        non_academic_summary = defaultdict(lambda: {"total": 0, "present": 0})
        for rec in non_academic_records:
            sid = rec["subject_id"]
            non_academic_summary[sid]["total"] += 1
            if student_id in rec["status"] and rec["status"][student_id] == "present":
                non_academic_summary[sid]["present"] += 1

        all_rates = []
        for stat in non_academic_summary.values():
            rate = (stat["present"] / stat["total"]) * 100 if stat["total"] else 0
            all_rates.append(rate)

        non_academic_attendance_rate = round(sum(all_rates) / len(all_rates), 2) if all_rates else 0

        ### ---- LMS Behavior ----
        behavior_records = list( behavioural_table.find({"student_id": student_id, "class_id": class_id}))
        if not behavior_records:
            lms_login_freq = 0
            avg_duration_hrs = 0
            resource_access_hrs = 0
        else:
            grouped = defaultdict(list)
            for record in behavior_records:
                day = record["accessBeginTime"][:10]
                grouped[day].append(record)

            login_days = len(grouped)
            login_count = sum(len(entries) for entries in grouped.values())
            total_minutes = sum(r.get("durationMinutes", 0) for r in behavior_records)

            lms_login_freq = round(login_count / login_days, 2) if login_days else 0
            avg_duration_hrs = round((total_minutes / login_days) / 60, 2) if login_days else 0
            resource_access_hrs = round((total_minutes / login_count) / 60, 2) if login_count else 0

        ### ---- Final Output ----
        features = {
            **lms_completion,
            **exam_averages,
            **assi_marks,
            "assi_late": assi_late_pct,
            "non_academic_attendance": non_academic_attendance_rate,
            "academic_attendance": academic_attendance_rate,
            "lms_login_freq_per_day": lms_login_freq,
            "lms_active_avg_hrs": avg_duration_hrs,
            "resource_access_avg_hrs": resource_access_hrs
        }

        df = pd.DataFrame([features])
        prediction = model.predict(df)[0]

        print("student_id:", student_id, "performance_score:", float(prediction))

        return features

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating model features: {str(e)}")
