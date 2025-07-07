from fastapi import APIRouter, HTTPException
from .database import assignment_table, submission_table, class_table, teacher_table, subject_table,student_table
from .database import academic_attendance_table, exam_table, non_academic_attendance_table, content_table, student_content_table
from ..schemas.teacher_dashboard import  all_uploaded_assignments, all_progress
from ..models.teacher_dashboard import ExamMarksResponse, StudentProgress
from bson.objectid import ObjectId
from typing import List
from datetime import datetime, timedelta
from collections import defaultdict


teacher_dashboard_router = APIRouter()

@teacher_dashboard_router.get("/{teacher_id}/assignments", response_model=List[dict])
async def get_uploaded_assignments(teacher_id: str):
    try:
        teacher = teacher_table.find_one({"teacher_id": teacher_id})

        if not teacher:
            raise HTTPException(status_code=404, detail=f"Teacher with ID {teacher_id} not found")
        
        subjects_classes = teacher.get("subjects_classes", [])
        if not subjects_classes:
            raise HTTPException(status_code=404, detail=f"No subjects/classes found for Teacher with ID {teacher_id}")

        assignment_timeline = []

        for entry in subjects_classes:
            subject_id = entry.get("subject_id")
            class_ids = entry.get("class_id", [])

            if not subject_id or not class_ids:
                continue

            subject = subject_table.find_one({"subject_id": subject_id})
            if not subject:
                continue

            for class_id in class_ids:
                class_details = class_table.find_one({"class_id": class_id})
                if not class_details:
                    continue

                class_name = class_details.get("class_name", class_id)
                total_students = student_table.count_documents({"class_id": class_id})

                assignments = assignment_table.find({
                    "subject_id": subject_id,
                    "class_id": class_id,
                    "teacher_id": teacher_id
                })

                for assignment in assignments:
                    deadline = assignment.get("deadline")
                    if isinstance(deadline, str):
                        try:
                            deadline = datetime.fromisoformat(deadline)
                        except:
                            deadline = None
                    
                    submission_count = submission_table.count_documents({
                        "assignment_id": assignment.get("assignment_id")
                    })

                    assignment_timeline.append({
                        "assignment_name": assignment.get("assignment_name"),
                        "subject_name": subject.get("subject_name"),
                        "class_name": class_name,
                        "deadline": deadline,
                        "submission_count": submission_count,
                        "total_students": total_students
                    })

        return all_uploaded_assignments(assignment_timeline)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving teacher assignments: {str(e)}")

@teacher_dashboard_router.get("/classes", response_model=dict)
def get_all_classes():
    try:
        classes_cursor = class_table.find({}, {"_id": 0, "class_id": 1, "class_name": 1})
        classes = list(classes_cursor)  # Use list() instead of await
        return {"classes": classes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch classes: {str(e)}")

    
@teacher_dashboard_router.get("/{class_id}/{exam_year}/exam-marks", response_model=List[ExamMarksResponse])
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

@teacher_dashboard_router.get("/{class_id}/student_progress", response_model=List[dict])
async def get_student_progress(class_id: str, year: int = None):
    try:
        if not year:
            year = datetime.now().year

        # class_details = class_table.find_one({"class_id": class_id})
        # if not class_details:
        #     raise HTTPException(status_code=404, detail="Class not found")

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
                if record_date.year == year and record['subject_id'] == "academic":
                    total_days += 1
                    if student_id in record["status"]:
                        if record["status"][student_id] == "present":
                            present_days += 1
            academic_attendance_rate = (present_days / total_days) * 100 if total_days else 0


            # --- Non- Academic Attendance ---
            total_days = 0
            present_days = 0

            for record in academic_attendance:
                record_date = datetime.strptime(record["date"], "%Y-%m-%d")
                if record_date.year == year and record['subject_id'] != "academic":
                    total_days += 1
                    if student_id in record["status"]:
                        if record["status"][student_id] == "present":
                            present_days += 1
            non_academic_attendance_rate = (present_days / total_days) * 100 if total_days else 0

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
                "non_academic_attendance_rate": round(non_academic_attendance_rate,2),
                "avg_academic_progress": round(avg_academic_progress, 2)
            })

        return student_progress

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving student progress: {str(e)}")

@teacher_dashboard_router.get("/weekly_attendance", response_model=List[dict])
async def get_weekly_attendance(
    class_id: str = "CLS013",
    year: int = datetime.now().year,
    week_num: int = datetime.now().isocalendar()[1]
    ):
    try:
        start_date = datetime.strptime(f"{year}-W{week_num-1}-1", "%Y-W%W-%w")
        end_date = start_date + timedelta(days=6)


        attendance_records = list(academic_attendance_table.find({
            "class_id": class_id,
            "subject_id": "academic",
            "date": {
                "$gte": start_date.strftime("%Y-%m-%d"),
                "$lte": end_date.strftime("%Y-%m-%d")
            }
        }))

        if not attendance_records:
            raise HTTPException(status_code=404, detail="No attendance records found")

        flattened_data = []

        for record in attendance_records:
            status_dict = record.get("status", {})
            present_count = sum(1 for s in status_dict.values() if s.lower() == "present")
            absent_count = sum(1 for s in status_dict.values() if s.lower() == "absent")

            flattened_data.append({
                "weekday": record["weekday"],
                "Present": present_count,
                "Absent": absent_count
            })

        return flattened_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving attendance data: {str(e)}")
    
@teacher_dashboard_router.get("/low-academic-attendance", response_model=List[dict])
async def get_low_attendance_students(threshold: float = 80.0):
    try:
        students = list(student_table.find({}))
        if not students:
            raise HTTPException(status_code=404, detail="No students found.")

        attendance_records = list(academic_attendance_table.find({"subject_id": "academic"}))
        if not attendance_records:
            raise HTTPException(status_code=404, detail="No academic attendance records found.")

        # Map: student_id -> {class_id, full_name, total_days, present_days}
        attendance_summary = defaultdict(lambda: {"class_id": "", "full_name": "", "total": 0, "present": 0})

        for record in attendance_records:
            date = datetime.strptime(record["date"], "%Y-%m-%d")
            if date.year != datetime.now().year:
                continue

            for student_id, status in record.get("status", {}).items():
                attendance_summary[student_id]["total"] += 1
                if status == "present":
                    attendance_summary[student_id]["present"] += 1

        low_attendance_list = []

        for student in students:
            sid = student["student_id"]
            if sid not in attendance_summary:
                continue  # No attendance data

            summary = attendance_summary[sid]
            summary["class_id"] = student.get("class_id", "")
            summary["full_name"] = student.get("full_name", f"{student.get('first_name', '')} {student.get('last_name', '')}".strip())

            total = summary["total"]
            present = summary["present"]
            attendance_pct = (present / total) * 100 if total > 0 else 0

            if attendance_pct < threshold:
                low_attendance_list.append({
                    "student_id": sid,
                    "full_name": summary["full_name"],
                    "class_id": summary["class_id"],
                    "attendance_rate": round(attendance_pct, 2)
                })

        return low_attendance_list

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving low attendance students: {str(e)}")
    
@teacher_dashboard_router.get("/low-attendance-count")
def get_low_attendance_student_count(threshold: float = 80.0):
    try:
        students = list(student_table.find({}))
        if not students:
            raise HTTPException(status_code=404, detail="No students found.")

        attendance_records = list(academic_attendance_table.find({"subject_id": "academic"}))
        if not attendance_records:
            raise HTTPException(status_code=404, detail="No academic attendance records found.")

        attendance_summary = defaultdict(lambda: {"total": 0, "present": 0})
        current_year = datetime.now().year

        for record in attendance_records:
            date = datetime.strptime(record["date"], "%Y-%m-%d")
            if date.year != current_year:
                continue

            for student_id, status in record.get("status", {}).items():
                attendance_summary[student_id]["total"] += 1
                if status == "present":
                    attendance_summary[student_id]["present"] += 1

        count = 0
        for student in students:
            sid = student["student_id"]
            if sid not in attendance_summary:
                continue

            total = attendance_summary[sid]["total"]
            present = attendance_summary[sid]["present"]
            attendance_rate = (present / total) * 100 if total > 0 else 0

            if attendance_rate < threshold:
                count += 1

        return {"low_attendance_student_count": count}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")





