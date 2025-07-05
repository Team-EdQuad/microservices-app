from fastapi import APIRouter, HTTPException

from .database import student_table, subject_table, content_table, student_content_table
from .database import assignment_table, submission_table, academic_attendance_table
from .database import exam_table, behavioural_table,student_login_table
from .database import perf_prediction_table
from .ml_model_loader import model, avg_model, imputer, explainer
from fastapi import APIRouter, HTTPException, Query
import google.generativeai as genai

genai.configure(api_key="AIzaSyBr8ZeUFqGUT9dF4N8j-DcJk8CoctyFfq0")
gemini_model = genai.GenerativeModel("models/gemini-2.5-pro")

from datetime import datetime, timedelta,timezone
from collections import defaultdict
import pandas as pd
import pytz

model_features_router = APIRouter()

def determine_risk_level(current_score, score_diff):
    if score_diff is None:  # No previous score exists
        if current_score >= 75:
            return "Low Risk"
        elif current_score >= 50:
            return "Medium Risk"
        else:
            return "High Risk"
    else:
        if score_diff < 0 and current_score < 70:
            return "High Risk (Declining)"
        elif score_diff < 0:
            return "Medium Risk (Declining)"
        elif current_score >= 75:
            return "Low Risk"
        elif current_score >= 50:
            return "Medium Risk"
        else:
            return "High Risk"

def predict_performance(features_dict: dict) -> float:
    df = pd.DataFrame([features_dict])
    prediction = model.predict(df)[0]
    return round(float(prediction), 2)

@model_features_router.get("/{student_id}/{class_id}/model-features")
async def get_model_features(student_id: str, class_id: str):
    try:
        print(f"Called endpoint with student_id={student_id} class_id={class_id}") 
        student = student_table.find_one({"student_id": student_id, "class_id": class_id})
        if not student:
            raise HTTPException(status_code=404, detail="Student not found in given class")

        subject_ids = student.get("subject_id", [])
        if not subject_ids or len(subject_ids) < 3:
            raise HTTPException(status_code=400, detail="At least 6 subjects are expected for modeling")

        ### ---- LMS Completion ----
        lms_completion = {}
        for i, subject_id in enumerate(subject_ids[:6]):
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
                    # sub_time = datetime.fromisoformat(submission["submit_time_date"]) if isinstance(submission["submit_time_date"], str) else submission["submit_time_date"]
                    # if deadline and sub_time > deadline:
                    #     late_count += 1
                    if isinstance(a["deadline"], str):
                        deadline = datetime.fromisoformat(a["deadline"])
                    else:
                        deadline = a["deadline"]
                    if deadline.tzinfo is None:
                        deadline = deadline.replace(tzinfo=timezone.utc)

                    if isinstance(submission["submit_time_date"], str):
                        sub_time = datetime.fromisoformat(submission["submit_time_date"])
                    else:
                        sub_time = submission["submit_time_date"]
                    if sub_time.tzinfo is None:
                        sub_time = sub_time.replace(tzinfo=timezone.utc)

                    if sub_time > deadline:
                        late_count += 1

            avg = (marks_total / marks_count) if marks_count else 0
            assi_marks[f"assi_sub{i+1}"] = round(avg, 2)

        assi_late_pct = late_count  if total_assignments else 0

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
            # lms_login_freq = 0
            # avg_duration_hrs = 0
            resource_access_hrs = 0
        else:
            grouped = defaultdict(list)
            for record in behavior_records:
                day = record["accessBeginTime"][:10]
                grouped[day].append(record)

            # login_days = len(grouped)
            login_count = sum(len(entries) for entries in grouped.values())
            total_minutes = sum(r.get("durationMinutes", 0) for r in behavior_records)

            # lms_login_freq = round(login_count / login_days, 2) if login_days else 0
            # avg_duration_hrs = round((total_minutes / login_days) / 60, 2) if login_days else 0
            resource_access_hrs = round((total_minutes / login_count) / 60, 2) if login_count else 0


       ## ----- LMS Login Frequency and Active Hours ----
        records = student_login_table.find({"student_id": "STU001"})
        for r in records:
            print("Login:", r.get("loginTime"), "Logout:", r.get("logoutTime"))

        login_days = set()
        total_duration_minutes = 0
        day_count = set()
        login_count = 0 

        for record in student_login_table.find({"student_id": student_id}):
            login_time = record.get("loginTime")
            logout_time = record.get("logoutTime")

            if not login_time:
                continue  # Skip invalid records

            try:
                login_dt = datetime.fromisoformat(login_time)
                login_day = login_dt.date()
                login_days.add(str(login_day))  
                login_count += 1  

                if logout_time:
                    logout_dt = datetime.fromisoformat(logout_time)
                    session_minutes = (logout_dt - login_dt).total_seconds() / 60
                else:
                    session_minutes = 15  # assume 15 min default

                total_duration_minutes += session_minutes
                day_count.add(login_day)
            except Exception:
                continue


        lms_login_freq = round(login_count / len(login_days), 2) if login_days else 0
        avg_duration_hrs = round((total_duration_minutes / len(day_count)) / 60, 2) if day_count else 0



        ### ---- Final Output ----
        features = {
            **lms_completion,
            **exam_averages,
            **assi_marks,
            "assi_late": assi_late_pct,
            "non-academic_attendance": non_academic_attendance_rate,
            "academic_attendance": academic_attendance_rate,
            "lms_login_freq_per_day": lms_login_freq,
            "lms_active_avg_hrs": avg_duration_hrs,
            "resource_access_avg_hrs": resource_access_hrs
        }
        
        df = pd.DataFrame([features])
        prediction = model.predict(df)[0]
        performance_score = float(prediction)
        print("student_id:", student_id, "performance_score:", performance_score)

        ## ------SHAP Values Calculation------
        X_input = pd.DataFrame([features])
        X_transformed = imputer.transform(X_input)
        X_transformed_df = pd.DataFrame(X_transformed, columns=X_input.columns)

        shap_values = explainer.shap_values(X_transformed_df)[0]

        top_shap_features = sorted(
            zip(X_input.columns, shap_values),
            key=lambda x: abs(x[1]),
            reverse=True
        )[:5]

        print("Top SHAP features:", top_shap_features)

        ## ------Exam Average Model Prediction------
        avg_features = {
            **lms_completion,
            **assi_marks,
            "assi_late": assi_late_pct,
            "non-academic_attendance": non_academic_attendance_rate,
            "academic_attendance": academic_attendance_rate,
            "lms_login_freq_per_day": lms_login_freq,
            "lms_active_avg_hrs": avg_duration_hrs,
            "resource_access_avg_hrs": resource_access_hrs
        }

        df2 = pd.DataFrame([avg_features])
        avg_prediction = float(avg_model.predict(df2)[0])

        print("student_id:", student_id, "Next Term Average Score:", float(avg_prediction))


        # === Get previous prediction for this student ===
        previous_entry = perf_prediction_table.find_one(
            {"student_id": student_id, "class_id": class_id},
            sort=[("timestamp", -1)] 
        )

        previous_score = previous_entry["score"] if previous_entry else None
        score_diff = float(performance_score - previous_score) if previous_score is not None else None

        risk_level = determine_risk_level(performance_score, score_diff)

        # === Store current prediction in collection ===
        perf_prediction_table.insert_one({
            "student_id": student_id,
            "class_id": class_id,
            "score": float(round(prediction, 2)),
            "next_term_avg": float(round(avg_prediction, 2)),
            "features": {k: float(v) if hasattr(v, "item") else v for k, v in features.items()},
            "top_shap_features": [
                {"feature": str(name), "impact": float(value)}
                for name, value in top_shap_features
            ],
            "timestamp": datetime.utcnow(),
            "score_diff": float(score_diff) if score_diff is not None else None,
            "risk_level": risk_level
        })


        return {
            "features": features,
            "performance_score": round(performance_score, 2),
            "next_term_avg_score": round(avg_prediction, 2),
            "risk_level": risk_level,
            "top_shap_features": [
                {"feature": str(name), "impact": float(value)}
                for name, value in top_shap_features
            ]
        }



    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating model features: {str(e)}")

@model_features_router.get("/{student_id}/{class_id}/ai-feedback")
async def get_gemini_feedback(student_id: str, class_id: str):
    try:
        prediction_record = perf_prediction_table.find_one(
            {"student_id": student_id, "class_id": class_id},
            sort=[("timestamp", -1)]
        )
        if not prediction_record:
            raise HTTPException(status_code=404, detail="No prediction record found")

        performance_score = prediction_record["score"]
        risk_level = prediction_record["risk_level"]
        next_term_avg = prediction_record.get("next_term_avg", 0)
        top_shap_features = prediction_record.get("top_shap_features", [])

        if not top_shap_features:
            raise HTTPException(status_code=500, detail="Top SHAP features not found in prediction record")

        feature_text = "\n".join([
            f"{item['feature']}: {item['impact']:+.2f}" for item in top_shap_features
        ])

        prompt = f"""
        You are an academic advisor assistant helping a student using the EdQuad LMS system to understand their predicted performance. Note that lms_sub1-6 are the subject content uploaded to LMS access rates.

        The student's current predicted performance score is {performance_score:.1f}, with a risk level of "{risk_level}".
        Their next term average academic score is predicted to be {next_term_avg:.1f}.

        Here are the most important SHAP features influencing the performance score:
        {feature_text}

        Explain clearly in simple language in short paragraphs:
        1. Why the student got this score
        2. What factors most affected it
        3. Give some personalized improvement suggestions in a para

        Keep your explanation concise, just start directly, no more than 150 words and do not use numbers coming with the feature names  (eg: lms_sub1 here one is unknown by student )as they are just model training feature naming.
        """

        response = gemini_model.generate_content(prompt)
        return {"feedback": response.text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating AI feedback: {str(e)}")
