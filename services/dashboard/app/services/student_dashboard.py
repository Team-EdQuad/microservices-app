from fastapi import APIRouter, HTTPException
from .database import student_table, subject_table, content_table, student_content_table
from .database import assignment_table, submission_table, academic_attendance_table
from .database import exam_table
from  ..schemas.student_dashboard import all_progress, all_assignments, academic_attendance_rate
from ..models.student_dashboard import SubjectProgress, SubjectAssignment, AcademicAttendanceRate, ExamMarksResponse
from bson.objectid import ObjectId
from typing import List
from datetime import datetime
from collections import defaultdict

student_dashboard_router = APIRouter()

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
        student = student_table.find_one({"student_id": student_id})

        if not student:
            raise HTTPException(status_code=404, detail=f"Student with ID {student_id} not found")
        
        
        if student.get("class_id") != class_id:
            raise HTTPException(status_code=404, detail=f"Student with ID {student_id} is not enrolled in class with ID {class_id}")
        
        student_subjects = student.get("subject_id" ,[])
     
        if not student_subjects:
            raise HTTPException(status_code=404, detail=f"No subjects found for Student with ID {student_id}")
        
        assignment_timeline = []
        

        for subject_id in student_subjects:
            subject = subject_table.find_one({"subject_id": subject_id})
            if not subject:
                continue 


            assignments = assignment_table.find({"subject_id":subject_id, "class_id": class_id })
            submissions = list(submission_table.find({"student_id": student_id, "class_id": class_id, "subject_id": subject_id}))
          

            for assignment in assignments:
                assignment["status"] = "Not Completed"
                for submission in submissions:
                    if submission["assignment_id"] == assignment["assignment_id"]:
                        assignment["status"] = "Completed"
                        break

                deadline = assignment.get("deadline")
                if isinstance(deadline, str):
                    deadline = datetime.fromisoformat(deadline)
                

               
                if assignment["status"] != "Completed":
                    if deadline and deadline < datetime.now():
                        assignment["status"] = "Overdue"

                    else :
                        assignment["status"] = "Upcoming"


                assignment_timeline.append({
                "assignment_name": assignment["assignment_name"],
                "subject_name": subject["subject_name"],
                "class_id": class_id,
                "deadline": deadline if deadline else None,
                "status": assignment["status"]
                })
           
        return all_assignments(assignment_timeline)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving student assignments: {str(e)}")
    
    

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
                print(record['subject_id'])
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
