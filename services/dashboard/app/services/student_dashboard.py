from fastapi import APIRouter, HTTPException
from .database import student_table, subject_table, content_table, student_content_table
from .database import assignment_table, submission_table, academic_attendance_table
from .database import exam_table, behavioural_table
from .database import collection31 ,collection32
from  ..schemas.student_dashboard import all_progress, all_assignments, academic_attendance_rate
from ..models.student_dashboard import SubjectProgress, SubjectAssignment, AcademicAttendanceRate, ExamMarksResponse
from bson.objectid import ObjectId
from typing import List
from datetime import datetime
from collections import defaultdict
import logging
import traceback

student_dashboard_router = APIRouter()

logger = logging.getLogger("dashboard_logger")
logger.setLevel(logging.DEBUG)

@student_dashboard_router.get("/{student_id}/{class_id}/progress", response_model=List[dict])
async def get_student_subject_progress(student_id: str, class_id: str):
    try:
        student = student_table.find_one({"student_id": student_id})

        if not student:
            raise HTTPException(status_code=404, detail=f"Student with ID {student_id} not found")
        
        if student.get("class_id") != class_id:
            raise HTTPException(status_code=404, detail=f"Student with ID {student_id} is not enrolled in class with ID {class_id}")
        
        student_subjects = student.get("subject_id" ,[])
     
        if not student_subjects:
            raise HTTPException(status_code=404, detail=f"No subjects found for Student with ID {student_id}")

        progress_list = []

        for subject_id in student_subjects:
            subject = subject_table.find_one({"subject_id": subject_id})

            if not subject:
                raise HTTPException(status_code=404, detail=f"Subject with ID {subject_id} not found")
            
            total_contents = content_table.count_documents({"subject_id": subject_id, "class_id": class_id})
            completed_contents = student_content_table.count_documents({"subject_id": subject_id, "student_id": student_id, "status": "Active", "class_id": class_id})
            progress_percentage = (completed_contents / total_contents) * 100 if total_contents > 0 else 0

            progress_list.append({
                "subject_id": subject_id,
                "class_id": class_id,
                "subject_name": subject["subject_name"],
                "total_content": total_contents,
                "completed_content": completed_contents,
                "progress_percentage": round(progress_percentage,2)
            })  

        return all_progress(progress_list)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving student progress: {str(e)}")
    

@student_dashboard_router.get("/{student_id}/{class_id}/assignments", response_model=List[dict])
async def get_student_assignments(student_id: str, class_id: str):
    try:
        logger.info(f"Fetching assignments for Student: {student_id}, Class: {class_id}")

        try:
            student = student_table.find_one({"student_id": student_id})
            if not student:
                logger.warning(f"Student not found: {student_id}")
                raise HTTPException(status_code=404, detail=f"Student with ID {student_id} not found")
            if student.get("class_id") != class_id:
                logger.warning(f"Class mismatch for student {student_id}")
                raise HTTPException(status_code=404, detail=f"Student with ID {student_id} is not enrolled in class {class_id}")
        except Exception as e:
            logger.exception("Error retrieving student data")
            raise

        try:
            student_subjects = student.get("subject_id", [])
            if not student_subjects:
                logger.warning(f"No subjects for student {student_id}")
                raise HTTPException(status_code=404, detail=f"No subjects found for student {student_id}")
        except Exception as e:
            logger.exception("Error accessing student subjects")
            raise

        assignment_timeline = []

        for subject_id in student_subjects:
            try:
                subject = subject_table.find_one({"subject_id": subject_id})
                if not subject:
                    logger.warning(f"Subject not found: {subject_id}")
                    continue
            except Exception as e:
                logger.exception(f"Error retrieving subject {subject_id}")
                continue

            try:
                assignments = assignment_table.find({"subject_id": subject_id, "class_id": class_id})
                submissions = list(submission_table.find({
                    "student_id": student_id,
                    "class_id": class_id,
                    "subject_id": subject_id
                }))
            except Exception as e:
                logger.exception(f"Error querying assignments or submissions for subject {subject_id}")
                continue

            for assignment in assignments:
                try:
                    assignment["status"] = "Not Completed"
                    for submission in submissions:
                        if submission.get("assignment_id") == assignment.get("assignment_id"):
                            assignment["status"] = "Completed"
                            break

                    deadline = assignment.get("deadline")
                    if isinstance(deadline, str):
                        try:
                            deadline = datetime.fromisoformat(deadline)
                        except ValueError as ve:
                            logger.warning(f"Invalid date format in assignment {assignment.get('assignment_id')}: {deadline}")
                            deadline = None

                    if assignment["status"] != "Completed":
                        if deadline and deadline < datetime.now():
                            assignment["status"] = "Overdue"
                        else:
                            assignment["status"] = "Upcoming"

                    assignment_timeline.append({
                        "assignment_id": assignment.get("assignment_id"),
                        "assignment_name": assignment.get("assignment_name"),
                        "subject_name": subject.get("subject_name"),
                        "class_id": class_id,
                        "deadline": deadline if deadline else None,
                        "status": assignment["status"]
                    })
                except Exception as e:
                    logger.exception(f"Error processing assignment {assignment.get('assignment_id')}")

        return all_assignments(assignment_timeline)

    except Exception as e:
        logger.exception("Unhandled error in get_student_assignments")
        raise HTTPException(status_code=500, detail=f"Error retrieving student assignments: {str(e)}")
# @student_dashboard_router.get("/{student_id}/{class_id}/assignments", response_model=List[dict])
# async def get_student_assignments(student_id: str, class_id: str):
#     try:
#         student = student_table.find_one({"student_id": student_id})

#         if not student:
#             raise HTTPException(status_code=404, detail=f"Student with ID {student_id} not found")
        
        
#         if student.get("class_id") != class_id:
#             raise HTTPException(status_code=404, detail=f"Student with ID {student_id} is not enrolled in class with ID {class_id}")
        
#         student_subjects = student.get("subject_id" ,[])
     
#         if not student_subjects:
#             raise HTTPException(status_code=404, detail=f"No subjects found for Student with ID {student_id}")
        
#         assignment_timeline = []
        

#         for subject_id in student_subjects:
#             subject = subject_table.find_one({"subject_id": subject_id})
#             if not subject:
#                 continue 


#             assignments = assignment_table.find({"subject_id":subject_id, "class_id": class_id })
#             submissions = list(submission_table.find({"student_id": student_id, "class_id": class_id, "subject_id": subject_id}))
          

#             for assignment in assignments:
#                 assignment["status"] = "Not Completed"
#                 for submission in submissions:
#                     if submission["assignment_id"] == assignment["assignment_id"]:
#                         assignment["status"] = "Completed"
#                         break

#                 deadline = assignment.get("deadline")
#                 if isinstance(deadline, str):
#                     deadline = datetime.fromisoformat(deadline)
                

               
#                 if assignment["status"] != "Completed":
#                     if deadline and deadline < datetime.now():
#                         assignment["status"] = "Overdue"

#                     else :
#                         assignment["status"] = "Upcoming"


#                 assignment_timeline.append({
#                 "assignment_id": assignment["assignment_id"],
#                 "assignment_name": assignment["assignment_name"],
#                 "subject_name": subject["subject_name"],
#                 "class_id": class_id,
#                 "deadline": deadline if deadline else None,
#                 "status": assignment["status"]
#                 })
           
#         return all_assignments(assignment_timeline)

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error retrieving student assignments: {str(e)}")
    
    

@student_dashboard_router.get("/{student_id}/{class_id}/assignments/filterByStatus", response_model=List[dict])
async def filter_assignments(student_id: str, class_id: str, status: str = None):
    try:
        list_of_assignments = await get_student_assignments(student_id, class_id)
        if not status:
            return list_of_assignments
        
        filtered_assignments = [assignment for assignment in list_of_assignments if assignment["status"] == status]
        return filtered_assignments
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error filtering assignments: {str(e)}")
    

@student_dashboard_router.get("/{student_id}/{class_id}/assignments/filterByDate", response_model=List[dict])
async def sort_assignments(student_id: str, class_id: str, status: str = None):
    try:
        if status:
            list_of_assignments = await filter_assignments(student_id, class_id, status)

        else:
            list_of_assignments = await get_student_assignments(student_id, class_id)
        
        for assignment in list_of_assignments:
            deadline = assignment.get("deadline")
            if isinstance(deadline, str):
                try:
                    assignment["deadline"] = datetime.fromisoformat(deadline)
                except ValueError:
                    assignment["deadline"] = datetime.max
            elif deadline is None:
                assignment["deadline"] = datetime.max
                
        sorted_timeline = sorted(list_of_assignments, key=lambda x: x["deadline"] )
        return sorted_timeline

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error filtering assignments: {str(e)}")   
    


@student_dashboard_router.get("/{student_id}/{class_id}/academicAttendanceRate", response_model=dict)
async def get_academic_attendance_rate(student_id: str, class_id: str):
    try:
        academic_attendance = list(academic_attendance_table.find({"class_id": class_id}))
        total_days = 0
        present_days = 0
        for record in academic_attendance:
            record_date = datetime.strptime(record["date"], "%Y-%m-%d")
            if record_date.year == datetime.now().year and record['subject_id'] == "academic":
                total_days += 1
                # for attendance_status in record["status"]:
                #     if attendance_status["student_id"] == student_id:
                #         if attendance_status["status"]:
                #             present_days += 1
                #         break

                if student_id in record["status"]:
                    if record["status"][student_id] == "present":
                        present_days += 1

        if total_days == 0:
            raise HTTPException(status_code=404, detail=f"No attendance records found for student ")

        attendance_rate = (present_days / total_days) * 100 if total_days > 0 else 0


        return academic_attendance_rate({
            "total_days": total_days,
            "days_present": present_days,
            "attendance_rate": round(attendance_rate,2)})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving academic attendance rate: {str(e)}")


@student_dashboard_router.get("/{student_id}/{class_id}/exam-marks", response_model=List[ExamMarksResponse])
async def get_student_exam_marks(student_id: str, class_id: str, exam_year: int = None):
    if not exam_year:
        exam_year = datetime.now().year - 1 

    student_exam_marks = exam_table.find_one({"student_id": student_id, "exam_year": exam_year, "class_id": class_id})
    
    if not student_exam_marks:
        raise HTTPException(status_code=404, detail="Student exam records not found")

    flattened_data = []
    for subject in student_exam_marks.get("exam_marks", []):
        subject_id = subject["subject_id"]
        subject_data = subject_table.find_one({"subject_id": subject_id})
        
        if subject_data:
            subject_name = subject_data["subject_name"]
            for exam in subject["exams"]:
                flattened_data.append({
                    "subject_name": subject_name,
                    "term": exam["term"],   
                    "marks": exam["marks"]
                })
    return flattened_data


@student_dashboard_router.get("/{student_id}/{class_id}/mothlyAttendanceRate", response_model=List[dict])
async def get_monthly_attendance_rate(student_id: str, class_id: str):
    try:
        monthly_attendance = defaultdict(lambda: {"total_days": 0, "present_days": 0})

        academic_attendance = list(academic_attendance_table.find({"class_id": class_id}))
        for record in academic_attendance:
            record_date = datetime.strptime(record["date"], "%Y-%m-%d")

            if record_date.year == datetime.now().year and record['subject_id'] == "academic":
                month = record_date.strftime("%B")
                monthly_attendance[month]["total_days"] += 1

                # for attendance_status in record["status"]:
                #     if attendance_status["student_id"] == student_id:
                #         if attendance_status["status"]:
                #             monthly_attendance[month]["present_days"] += 1
                #         break
                if student_id in record["status"]:
                    if record["status"][student_id] == "present":
                        monthly_attendance[month]["present_days"] += 1

        if not monthly_attendance:
            raise HTTPException(status_code=404, detail="No attendance records found.")
        
        monthly_attendance_data = []
        for month, data in monthly_attendance.items():
            attendance_rate = (data["present_days"] / data["total_days"]) * 100 if data["total_days"] > 0 else 0
            monthly_attendance_data.append({
                "month": month,
                "attendance_rate": round(attendance_rate, 2)
            })

        month_order = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        monthly_attendance_data.sort(key=lambda x: month_order.index(x["month"]))
        return monthly_attendance_data


    except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving monthly attendance rate: {str(e)}")
    

@student_dashboard_router.get("/{student_id}/{class_id}/weeklyAttendanceRate", response_model=List[dict])
async def get_weekly_attendance_rate(student_id: str, class_id: str):
    try:
        weekly_attendance = defaultdict(lambda: {"total_days": 0, "present_days": 0})
        attendance_records = list(academic_attendance_table.find({"class_id": class_id}))

        for record in attendance_records:
            record_date = datetime.strptime(record["date"], "%Y-%m-%d")
            
            if record_date.year == datetime.now().year and record['subject_id'] == "academic":
                weekday = record["weekday"]

                weekly_attendance[weekday]["total_days"] += 1

                if student_id in record["status"]:
                    if record["status"][student_id] == "present":
                        weekly_attendance[weekday]["present_days"] += 1

        if not weekly_attendance:
            raise HTTPException(status_code=404, detail="No attendance records found.")

        weekly_data = []
        for weekday, data in weekly_attendance.items():
            attendance_rate = (data["present_days"] / data["total_days"]) * 100 if data["total_days"] > 0 else 0
            weekly_data.append({
                "weekday": weekday,
                "attendance_rate": round(attendance_rate, 2)
            })


        weekday_order = [
            "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
        ]   
        weekly_data.sort(key=lambda x: weekday_order.index(x["weekday"]))
        return weekly_data
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving weekly attendance rate: {str(e)}")


@student_dashboard_router.get("/{student_id}/{class_id}/nonacademic-attendance")
async def get_student_nonacademic_attendance(student_id: str, class_id: str):
    current_year = str(datetime.now().year)

    student = student_table.find_one({"student_id": student_id, "class_id": class_id})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    sport_ids = student.get("sport_id", [])
    club_ids = student.get("club_id", [])
    activity_ids = sport_ids + club_ids

    attendance_records = academic_attendance_table.find({
        "class_id": class_id,
        "subject_id": {"$in": activity_ids},
        "date": {"$regex": f"^{current_year}"} 
    })

    
    attendance_summary = {aid: {"present": 0, "total": 0} for aid in activity_ids}

    for record in attendance_records:
        subject_id = record["subject_id"]
        if student_id in record["status"]:
            attendance_summary[subject_id]["total"] += 1
            if record["status"][student_id] == "present":
                attendance_summary[subject_id]["present"] += 1

    results = []
    for aid, counts in attendance_summary.items():
        name = ""
        if aid in sport_ids:
            sport = collection31.find_one({"sport_id": aid})
            name = sport["sport_name"] if sport else aid
        else:
            club = collection32.find_one({"club_id": aid})
            name = club["club_name"] if club else aid

        total = counts["total"]
        present = counts["present"]
        absent = total - present
        present_pct = round((present / total) * 100, 2) if total else 0
        absent_pct = round((absent / total) * 100, 2) if total else 0

        results.append({
            "name": name,
            "present": present_pct,
            "absent": absent_pct
        })

    return {"activities_attendance": results}

@student_dashboard_router.get("/{student_id}/{class_id}/engagement-score")
def calculate_engagement_score(student_id: str, class_id: str):
    try:
        student = student_table.find_one({"student_id": student_id})
        if not student or student.get("class_id") != class_id:
            raise HTTPException(status_code=404, detail="Student not found or not in class")

        subject_ids = student.get("subject_id", [])
        if not subject_ids:
            return {"engagement_score": 0}

        total_contents = content_table.count_documents({
            "class_id": class_id,
            "subject_id": {"$in": subject_ids}
        })

        if total_contents == 0:
            return {"engagement_score": 0}
        
        completed = student_content_table.count_documents({
            "student_id": student_id,
            "class_id": class_id,
            "status": "Active"
        })
        completion_rate = (completed / total_contents) * 100

        behavioural_records = list(behavioural_table.find({
            "student_id": student_id,
            "class_id": class_id,
            "subject_id": {"$in": subject_ids}
        }))

        total_duration = sum([rec.get("durationMinutes", 0) for rec in behavioural_records])
        total_accesses = sum([rec.get("accessCount", 0) for rec in behavioural_records])
        unique_contents = len(set([rec["content_id"] for rec in behavioural_records]))

        avg_duration = total_duration / unique_contents if unique_contents else 0
        avg_access = total_accesses / unique_contents if unique_contents else 0

        time_score = min((avg_duration / 10) * 100, 100)
        frequency_score = min((avg_access / 3) * 100, 100)

        engagement_score = (
            0.5 * completion_rate +
            0.3 * time_score +
            0.2 * frequency_score
        )

        return {"engagement_score": round(engagement_score, 2)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
