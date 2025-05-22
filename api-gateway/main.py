import sys
import os
from datetime import datetime, timedelta
import httpx 
from fastapi.responses import JSONResponse
from typing import List, Optional
from fastapi import Depends,Request

# from services.attendance.app.utils import schemas as attModSchemas

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'services')))

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, APIRouter, Body, UploadFile, File, Form
from services.nonacademic import get_all_sports, create_sport, get_all_clubs, create_club, filter_sports
from services.dashboard import get_student_progress, get_student_assignments,filter_assignments,sort_assignments, get_student_attendance,get_student_exam_marks,monthly_attendance, current_weekly_attendance,non_academic_attendance,engagement_score
from services.dashboard import get_teacher_assignments, get_exam_marks_teacher, get_student_progress_teacher, get_weekly_attendance,get_all_Classes
from services.dashboard import get_exam_marks_admin,  get_student_progress_admin, get_weekly_attendance_admin, get_stats, get_all_users

from services.usermanagement import login_user, get_current_user

from schemas.usermanagement import LoginRequest


from services.academic import  get_assignment_file_by_id,get_content_by_id,get_content_file_by_id,create_assignment_request,upload_content_request,view_ungraded_manual_submissions,update_manual_marks,add_exam_marks_request,get_subject_names,get_student_content,get_all_assignments,get_assignment_by_id,get_assignment_marks,get_exam_marks, upload_assignment_file ,mark_content_done,get_subject_and_class_for_teacher
from services.behavioural import time_spent_on_resources,average_active_time,resource_access_frequency,content_access_start,content_access_close

from services.attendance import attendanceRouter

app = FastAPI(title="Microservices API Gateway") 

# app.include_router(attendanceRouter)




app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Frontend URL
    # allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# User-management
@app.post("/api/user-management/login")
async def login_user(credentials: LoginRequest):
    return await login_user(credentials.dict())

# @app.get("/api/user-management/user-data")
# async def get_user_data(request: Request):
#     current_user = await get_current_user(request)
#     if current_user["role"] == "admin":
#         return {"message": "Admin data", "data": current_user}

#non-academic
@app.get("/api/nonacademic/sports", response_model=list)
async def fetch_all_sports():
    return await get_all_sports()

@app.post("/api/nonacademic/sports", response_model=dict)
async def add_sport(sport: dict):
    return await create_sport(sport)

# Academic
@app.get("/api/content/{content_id}")
async def get_content_file(content_id: str):
    return await get_content_by_id(content_id)

@app.get("/api/content/file/{content_id}")
async def get_content_file(content_id: str):
    return await get_content_file_by_id(content_id)


@app.get("/api/assignment/file/{assignment_id}")
async def get_content_file(assignment_id: str):
    return await get_assignment_file_by_id(assignment_id)



@app.get("/api/subject/{student_id}", response_model=List)
async def get_subjects(student_id: str):
    return await get_subject_names(student_id)


@app.get("/api/content/{student_id}/{subject_id}", response_model=List)
async def get_content(student_id: str, subject_id: str):
    return await get_student_content(student_id, subject_id)


@app.get("/api/assignments/{student_id}/{subject_id}")
async def get_assignments(student_id: str, subject_id: str):   
    try:
        return await get_all_assignments(student_id, subject_id)
    except HTTPException as exc:
        raise exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(exc)}")


@app.get("/api/assignment/{assignment_id}")
async def get_assignment_details(assignment_id: str):
    assignment = await get_assignment_by_id(assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return assignment


@app.get("/api/assignmentmarks/{student_id}")
async def fetch_assignment_marks(student_id: str):
    return await get_assignment_marks(student_id)
    
@app.get("/api/exammarks/{student_id}")
async def fetch_exam_marks(student_id: str):
    return await get_exam_marks(student_id)
    




@app.post("/api/submission/{student_id}/{assignment_id}")
async def submit_assignment_file(
    student_id: str,
    assignment_id: str,
    file: UploadFile = File(...)
):
    result = await upload_assignment_file(student_id, assignment_id, file)
    return {"message": "Submission successful", "data": result}

@app.post("/api/content/{content_id}")
async def mark_content_completed(content_id: str):
    success = await mark_content_done(content_id)
    if not success:
        raise HTTPException(status_code=404, detail="Content not found or not accessible")
    return {"message": "Content marked as completed"}


###teacher 

@app.get("/api/subjectNclass/{teacher_id}")
async def get_subject_and_class(teacher_id: str):
    return await get_subject_and_class_for_teacher(teacher_id)
@app.post("/api/assignmentcreate/{class_id}/{subject_id}/{teacher_id}")
async def create_assignment(
    class_id: str,
    subject_id: str,
    teacher_id: str,
    assignment_name: str = Form(...),
    description: str = Form(...),
    deadline: str = Form(...),  # Should be in ISO format!
    grading_type: str = Form(...),
    sample_answer: Optional[str] = Form(None),
    file: UploadFile = File(...)
):
    form_data = {
        "assignment_name": assignment_name,
        "description": description,
        "deadline": deadline,
        "grading_type": grading_type,
        "sample_answer": sample_answer
    }

    return await create_assignment_request(class_id, subject_id, teacher_id, form_data, file)

@app.post("/api/contentupload/{class_id}/{subject_id}")
async def upload_content(
    class_id: str,
    subject_id: str,
    content_name: str = Form(...),
    description: str = Form(...),
    file: UploadFile = File(...)
):
    return await upload_content_request(class_id, subject_id, content_name, description, file)


@app.get("/api/submission_view/{teacher_id}", response_model=List)
async def get_manual_submissions(teacher_id: str):
    return await view_ungraded_manual_submissions(teacher_id)


@app.post("/api/update_submission_marks/{teacher_id}")
async def update_submission_marks(
    teacher_id: str,
    submission_id: str = Form(...),
    marks: float = Form(...)
):
    return await update_manual_marks(teacher_id, submission_id, marks)


@app.post("/api/update_exam_marks")
async def update_exam_marks(
    teacher_id: str = Form(...),
    student_id: str = Form(...),
    exam_year: int = Form(...),
    subject_name: str = Form(...),  # Only send name
    term: int = Form(...),
    marks: float = Form(...),
):
    exam_type = f"Term {term}"

    form_data = {
        "teacher_id": teacher_id,
        "student_id": student_id,
        "exam_year": exam_year,
        "subject_name": subject_name,  # Let academic service resolve subject_id
        "term": term,
        "exam_type": exam_type,
        "marks": marks
    }

    return await add_exam_marks_request(form_data)




### behavioral


@app.get("/api/TimeSpendOnResources/{subject_id}/{class_id}")
async def get_time_spent_on_resources(subject_id: str, class_id: str):
    return await time_spent_on_resources(subject_id, class_id)


@app.get("/api/SiteAverageActiveTime/{class_id}")
async def get_site_average_active_time(class_id: str):
    return await average_active_time(class_id)


@app.get("/api/ResourceAccessFrequency/{subject_id}/{class_id}")
async def get_resource_access_frequency(subject_id: str, class_id: str):
   return await resource_access_frequency(subject_id, class_id)


@app.post("/api/startContentAccess")
async def start_content_access(
    student_id: str = Form(...),
    content_id: str = Form(...)
):
    return await content_access_start(student_id, content_id)

@app.post("/api/closeContentAccess")
async def close_content_access(
    student_id: str = Form(...),
    content_id: str = Form(...)
):
    return await content_access_close(student_id, content_id)



#Student Dashboard Routes
@app.get("/api/dashboard/{student_id}/{class_id}/progress")
async def dashboard_progress(student_id: str, class_id: str):
    try:
        return await get_student_progress(student_id, class_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/{student_id}/{class_id}/assignments")
async def dashboard_assignments(student_id: str, class_id: str):
    try:
        return await get_student_assignments(student_id, class_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/api/dashboard/{student_id}/{class_id}/assignments/filterByStatus")
async def filter_assignments_timeline(student_id: str, class_id: str, status: str = None):
    try:
        return await filter_assignments(student_id, class_id, status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/{student_id}/{class_id}/assignments/filterByDate")
async def sort_assignments_timeline(student_id: str, class_id: str, status: str = None):
    try:
        return await sort_assignments(student_id, class_id, status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/{student_id}/{class_id}/academicAttendanceRate")
async def dashboard_attendance(student_id: str, class_id: str):
    try:
        return await get_student_attendance(student_id, class_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/{student_id}/{class_id}/exam-marks")
async def dashboard_non_academic(student_id: str, class_id: str, exam_year: int = None):
    try:
        return await get_student_exam_marks(student_id, class_id, exam_year)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/api/dashboard/{student_id}/{class_id}/mothlyAttendanceRate")
async def dashboard_monthly_attendance(student_id: str, class_id: str):
    try:
        return await monthly_attendance(student_id, class_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.get("/api/dashboard/{student_id}/{class_id}/weeklyAttendanceRate")
async def dashboard_weekly_attendance(student_id: str, class_id: str):
    try:
        return await current_weekly_attendance(student_id, class_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/api/dashboard/{student_id}/{class_id}/nonacademic-attendance")
async def dashboard_non_academic_attendance(student_id: str, class_id: str):
    try:
        return await  non_academic_attendance(student_id, class_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/api/dashboard/{student_id}/{class_id}/engagement-score")
async def dashboard_engagement_score(student_id: str, class_id: str):
    try:
        return await  engagement_score(student_id, class_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#Teacher Dashboard Routes
@app.get("/api/teacher/dashboard/{teacher_id}/assignments")
async def teacher_assignments(teacher_id: str):
    try:
        return await get_teacher_assignments(teacher_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/api/teacher/dashboard/classes")
async def get_all_classes():
    try:
        return await get_all_Classes()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/teacher/dashboard/{class_id}/{exam_year}/exam-marks")
async def exam_marks(class_id: str, exam_year: int):
    try:
        return await get_exam_marks_teacher(class_id, exam_year)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/api/teacher/dashboard/{class_id}/progress")
async def student_progress_teacher(class_id: str, year:int = None):
    try:
        return await get_student_progress_teacher(class_id,year)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/api/teacher/dashboard/weekly_attendance")
async def weekly_attendance(class_id: str = "CLS001", year: int = datetime.now().year, week_num: int = datetime.now().isocalendar()[1]):
    try:
        return await get_weekly_attendance(class_id, year, week_num)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#Admin Dashboard Routes
@app.get("/api/admin/dashboard/users")
async def users(search_with_id: str = None, role: str = None, class_id: str = None):
    try:
        return await get_all_users(search_with_id, role, class_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/api/admin/dashboard/stats")
async def stats():
    try:
        return await get_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/dashboard/{class_id}/{exam_year}/exam-marks")
async def exam_marks_admin(class_id: str, exam_year: int):
    try:
        return await get_exam_marks_admin(class_id, exam_year)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.get("/api/admin/dashboard/{class_id}/progress")
async def student_progress_admin(class_id: str):
    try:
        return await get_student_progress_admin(class_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/api/admin/dashboard/weekly_attendance")  
async def weekly_attendance_admin(class_id: str = "CLS001", year: int = datetime.now().year, week_num: int = datetime.now().isocalendar()[1]):
    try:
        return await get_weekly_attendance_admin(class_id, year, week_num)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    

#Attendance
app.include_router(attendanceRouter)
    

