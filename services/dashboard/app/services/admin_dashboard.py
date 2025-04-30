from fastapi import APIRouter, HTTPException, Query
from .database import class_table, teacher_table, subject_table, student_table, student_login_table,admin_table
from .database import academic_attendance_table, exam_table, non_academic_attendance_table, content_table, student_content_table
from ..schemas.admin_dashboard import all_progress, stats
from ..models.admin_dashboard import ExamMarksResponse, StudentProgress, UserLite
from bson.objectid import ObjectId
from typing import List, Optional
from datetime import datetime, timedelta

admin_dashboard_router = APIRouter()


@admin_dashboard_router.get("/user_data", response_model=List[UserLite])
async def get_user_profiles(
    search_with_id: Optional[str] = Query(None),
    role: Optional[str] = Query(None, description="student | teacher | admin"),
    class_id: Optional[str] = Query(None)
    ):
    users =[]

    role_collection = {
        "student": student_table,
        "teacher": teacher_table,
        "admin": admin_table
    }
    roles_to_check = [role] if role in role_collection else role_collection.keys()

    for r in roles_to_check:
        table  = role_collection[r]
        query = {}

        if search_with_id:

            
            query["student_id" if r == "student" else "teacher_id" if r == "teacher" else "admin_id"] = {
                "$regex": f"^{search_with_id}" , "$options": "i"
            }
        
        if class_id and r in ["student", "teacher"]:
            query["class_id"] = class_id

        results = list(table.find(query))

        for user in results:
            users.append(UserLite(
                user_id=user.get("student_id") or user.get("teacher_id") or user.get("admin_id"),
                full_name=user.get("full_name", "Unknown"),
                role=r
            ))

    return users

@admin_dashboard_router.get("/stats", response_model=dict[str,  int])
async def get_students_by_class():
    try:
        student_count = student_table.count_documents({})
        teacher_count = teacher_table.count_documents({})
        active_today = student_login_table.count_documents({"login_time": {"$gte": datetime.now() - timedelta(days=1)}})

        data= {
            "total_students": student_count,
            "total_teachers": teacher_count,
            "active_students_today": active_today
        }
        return stats(data)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving statistics: {str(e)}")

    
@admin_dashboard_router.get("/{class_id}/{exam_year}/exam-marks", response_model=List[ExamMarksResponse])
async def get_class_exam_marks(class_id: str, exam_year: int):
    try:
        all_student_exam_marks = exam_table.find({"class_id": class_id, "exam_year": exam_year})
        
        if not all_student_exam_marks:
            raise HTTPException(status_code=404, detail="Class exam records not found")

        flattened_data=[]
        subject_term_marks = {}

        for student_exam_marks in all_student_exam_marks:
            for subject in student_exam_marks["exam_marks"]:
                subject_id = subject["subject_id"]
                subject_data = subject_table.find_one({"subject_id" : subject_id})
                subject_name = subject_data["subject_name"]
            
                if subject_name not in subject_term_marks:
                        subject_term_marks[subject_name] = {}
                    
                for exam in subject["exams"]:
                    term = exam["term"]
                    marks = exam["marks"]
            
                    if term not in subject_term_marks[subject_name]:
                        subject_term_marks[subject_name][term] = {"total_marks": 0, "count": 0}
            
                    subject_term_marks[subject_name][term]["total_marks"] += marks
                    subject_term_marks[subject_name][term]["count"] += 1

        average_marks = {}
        for subject, terms in  subject_term_marks.items():
            average_marks[subject] = {
                term: terms[term]["total_marks"] /  terms[term]["count"] for term in terms
            }

        for subject, terms in average_marks.items():
            for term, marks in terms.items():
                flattened_data.append({
                    "subject_name": subject,
                    "term": term,
                    "marks": marks
                })
    
        return flattened_data
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving class exam marks: {str(e)}")

@admin_dashboard_router.get("/{class_id}/student_progress", response_model=List[dict])
async def get_student_progress(class_id: str, year: int = None):
    try:
        if not year:
            year = datetime.now().year

        class_details = class_table.find_one({"class_id": class_id})
        if not class_details:
            raise HTTPException(status_code=404, detail="Class not found")

        all_students = list(student_table.find({"class_id": class_id}))
        academic_attendance = list(academic_attendance_table.find({"class_id": class_id}))

        if not all_students:
            raise HTTPException(status_code=404, detail="No students found in this class")

        student_progress = []

        for student in all_students:
            student_id = student["student_id"]
            student_name = student.get("full_name", "Unknown")

            # --- Exam Averages ---
            first_term_total = second_term_total = third_term_total = 0
            term1_count = term2_count = term3_count = 0

            student_exam_marks = exam_table.find_one({
                "student_id": student_id,
                "class_id": class_id,
                "exam_year": year
            })

            if student_exam_marks and student_exam_marks.get("exam_marks"):
                for subject in student_exam_marks["exam_marks"]:
                    for exam in subject.get("exams", []):
                        term = exam.get("term")
                        marks = exam.get("marks", 0)

                        if term == 1:
                            first_term_total += marks
                            term1_count += 1
                        elif term == 2:
                            second_term_total += marks
                            term2_count += 1
                        elif term == 3:
                            third_term_total += marks
                            term3_count += 1

            first_term_avg = first_term_total / term1_count if term1_count else 0
            second_term_avg = second_term_total / term2_count if term2_count else 0
            third_term_avg = third_term_total / term3_count if term3_count else 0

            # --- Academic Attendance ---
            total_days = 0
            present_days = 0
            for record in academic_attendance:
                record_date = datetime.strptime(record["date"], "%Y-%m-%d")
                if record_date.year == year:
                    total_days += 1
                    for status in record.get("status", []):
                        if status["student_id"] == student_id and status["status"]:
                            present_days += 1
                            break
            academic_attendance_rate = (present_days / total_days) * 100 if total_days else 0

            # --- Academic Progress ---
            avg_academic_progress = 0
            subject_ids = student.get("subject_id", [])
            if subject_ids:
                progress_rate = 0
                counted_subjects = 0

                for subject_id in subject_ids:
                    total_contents = content_table.count_documents({
                        "subject_id": subject_id,
                        "class_id": class_id,
                        "Date": {"$regex": f"^{year}-"}
                    })

                    if total_contents == 0:
                        continue

                    completed_contents = 0
                    contents = content_table.find({
                        "subject_id": subject_id,
                        "class_id": class_id,
                        "Date": {"$regex": f"^{year}-"}
                    })

                    for content in contents:
                        content_id = content.get("content_id")
                        student_content = student_content_table.find_one({
                            "content_id": content_id,
                            "student_id": student_id,
                            "status": "Active",
                            "class_id": class_id
                        })
                        if student_content:
                            completed_contents += 1

                    progress_percentage = (completed_contents / total_contents) * 100
                    progress_rate += progress_percentage
                    counted_subjects += 1

                avg_academic_progress = progress_rate / counted_subjects if counted_subjects else 0

            # --- Add Student Progress Entry ---
            student_progress.append({
                "student_name": student_name,
                "first_term_avg": round(first_term_avg, 2),
                "second_term_avg": round(second_term_avg, 2),
                "third_term_avg": round(third_term_avg, 2),
                "academic_attendance_rate": round(academic_attendance_rate, 2),
                "non_academic_attendance_rate": 0.0,  # Not implemented
                "avg_academic_progress": round(avg_academic_progress, 2)
            })

        return student_progress

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving student progress: {str(e)}")


@admin_dashboard_router.get("/weekly_attendance", response_model=List[dict])
async def get_weekly_attendance(class_id: str = "CLS001", year: int = datetime.now().year, week_num: int = datetime.now().isocalendar()[1]):
    try:
        start_date = datetime.strptime(f"{year}-W{week_num-1}-1", "%Y-W%W-%w")
        end_date = start_date + timedelta(days=6)

        attendance_records = list(academic_attendance_table.find({
            "class_id": class_id,
            "date": {"$gte": start_date.strftime("%Y-%m-%d"), "$lte": end_date.strftime("%Y-%m-%d")}
        }))

        if not attendance_records:
            raise HTTPException(status_code=404, detail="Attendance records not found")
        
        flattened_data = []

        for record in attendance_records:
            day = record["weekday"]
            present_ratio = record["present_ratio"]
            absent_ratio = record["absent_ratio"]
            total_students = len(record["status"])  

            present_count = round(present_ratio * total_students)
            absent_count = round(absent_ratio * total_students)

            flattened_data.append({
                "weekday": day,
                "Present": present_count,
                "Absent": absent_count
            })

        return flattened_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving attendance data: {str(e)}")
