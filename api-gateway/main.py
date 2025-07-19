import sys
import os
from datetime import datetime, timedelta
import httpx 
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional, Any
from fastapi import Depends,Request,Body,Form
from fastapi.security import OAuth2PasswordBearer
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles 
from fastapi import Query, Depends, Header
from datetime import date
import logging
import traceback


import json

from pydantic import BaseModel
# from services.attendance.app.utils import schemas as attModSchemas

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'services')))

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, APIRouter, Body, UploadFile, File, Form
from services.nonacademic import get_all_sports, create_sport, get_all_clubs, create_club, filter_sports
from services.dashboard import get_student_progress, get_student_assignments,filter_assignments,sort_assignments, get_student_attendance,get_student_exam_marks,monthly_attendance, current_weekly_attendance,non_academic_attendance,engagement_score, model_features,get_model_feedback
from services.dashboard import get_teacher_assignments, get_exam_marks_teacher, get_student_progress_teacher, get_weekly_attendance,get_all_Classes,get_low_attendance_students,get_low_attendance_students_count
from services.dashboard import get_exam_marks_admin,  get_student_progress_admin, get_weekly_attendance_admin, get_stats, get_all_users,forward_admin_access_profile

from services.usermanagement import login_user, add_admin, add_student, add_teacher, delete_user,edit_profile, update_password, get_profile, serialize_dates,logout_user,fetch_anomaly_results,update_student,proxy_get_student_data,proxy_get_full_profile

from schemas.usermanagement import LoginRequest, AdminCreate,StudentRegistration,TeacherCreate, UserProfileUpdate, UpdatePasswordRequest,UpdateStudentModel
from services.calendar import get_assignment_deadlines
from services.usermanagement import delete_user, get_recent_users_from_user_management # <-- THIS LINE NEEDS TO INCLUDE IT


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user-management/login")


from services.academic import  get_content_file_by_id,view_auto_graded_submissions_request,review_auto_graded_marks_request,get_student_list_by_class_and_subject,get_submission_file_by_id,get_assignment_file_by_id,create_assignment_request,upload_content_request,view_ungraded_manual_submissions,update_manual_marks,add_exam_marks_request,get_subject_names,get_student_content,get_all_assignments,get_assignment_by_id,get_assignment_marks,get_exam_marks, upload_assignment_file ,mark_content_done,get_subject_and_class_for_teacher
from services.behavioural import update_collection_active_time,call_prediction_service,model_train,Visualize_data_list,time_spent_on_resources,average_active_time,resource_access_frequency,content_access_start,content_access_close

from services.attendance import attendanceRouter


app = FastAPI(title="Microservices API Gateway") 

app.mount("/static", StaticFiles(directory="static"), name="static")

# app.include_router(attendanceRouter)





app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# User-management
# @app.post("/api/user-management/login/")
# async def api_login(username: str = Form(...), password: str = Form(...)):
#     credentials = {"username": username, "password": password}
#     return await login_user(credentials)
@app.post("/api/user-management/login/")
async def api_login(req: Request, username: str = Form(...), password: str = Form(...)):
    credentials = {"username": username, "password": password}
    return await login_user(req, credentials)  # ✅ Pass request

@app.post("/api/user-management/logout")
async def api_logout(
    user_id: str = Form(...),
    role: str = Form(...),
    token: str = Depends(oauth2_scheme)
):
    authorization = f"Bearer {token}"
    return await logout_user(user_id, role, authorization)


@app.post("/api/user-management/add-student")
async def api_add_student(
    student_data: StudentRegistration,
    token: str = Depends(oauth2_scheme)
):
    authorization = f"Bearer {token}"
    return await add_student(student_data.dict(), authorization)

@app.post("/api/user-management/add-admin")
async def api_add_admin(admin_data: AdminCreate, token: str = Depends(oauth2_scheme)):
    admin_dict = admin_data.dict()
    admin_dict = serialize_dates(admin_dict)
    return await add_admin(admin_dict, authorization=f"Bearer {token}")

@app.post("/api/user-management/add-teacher")
async def api_add_teacher(
    teacher_data: TeacherCreate,
    token: str = Depends(oauth2_scheme)
):
    authorization = f"Bearer {token}"
    data_dict = teacher_data.dict()
    return await add_teacher(data_dict, authorization)

@app.delete("/api/user-management/delete-user/{role}/{user_custom_id}")
async def api_delete_user(role: str, user_custom_id: str, token: str = Depends(oauth2_scheme)):
    authorization = f"Bearer {token}"
    return await delete_user(role, user_custom_id, authorization)

@app.get("/api/user-management/get-student/{student_id}")
async def api_get_student_data(student_id: str, request: Request):
    # Just forward the whole request to proxy
    return await proxy_get_student_data(student_id, request)

@app.post("/api/user-management/update-student/")
async def gateway_update_student(
    student_data: UpdateStudentModel,
    authorization: Optional[str] = Header(None)
):
    return await update_student(student_data, authorization)

# API Gateway endpoint for recent users
@app.get("/api/user-management/recent-users/{role}")
async def api_get_recent_users(role: str, token: str = Depends(oauth2_scheme)): # Assuming recent users also need auth
    authorization = f"Bearer {token}"
    return await get_recent_users_from_user_management(role, authorization) # Call the service function

@app.put("/api/user-management/edit-profile/{role}/{user_id}")
async def api_edit_profile(
    role: str,
    user_id: str,
    profile_update: UserProfileUpdate,
    token: str = Depends(oauth2_scheme)
):
    authorization = f"Bearer {token}"
    profile_dict = profile_update.dict()
    return await edit_profile(role, user_id, profile_dict, authorization)

@app.put("/api/user-management/update-password")
async def api_update_password(
    password_update: UpdatePasswordRequest,
    token: str = Depends(oauth2_scheme)
):
    authorization = f"Bearer {token}"
    return await update_password(password_update.dict(), authorization)

@app.get("/api/user-management/profile")
async def profile(token: str = Depends(oauth2_scheme)):
    print(f"Received token in API Gateway: {token}")
    auth_header = f"Bearer {token}"
    profile_data = await get_profile(authorization=auth_header)
    print(f"Profile data response: {profile_data}")
    return profile_data

@app.get("/api/user-management/get-full-profile")
async def get_full_profile_proxy(request: Request, token: str = Depends(oauth2_scheme)):
    auth_header = f"Bearer {token}"
    return await proxy_get_full_profile(request, authorization=auth_header)


@app.get("/api/anomaly-detection/results")
async def api_get_anomaly_results(
    username: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    token: str = Depends(oauth2_scheme)
):
    # authorization = f"Bearer {token}"
    from services.usermanagement import fetch_anomaly_results
    return await fetch_anomaly_results(username, role, token)

# MODIFIED ANOMALY DETECTION RESULTS ENDPOINT IN API GATEWAY
# @app.get("/api/anomaly-detection/results")
# async def api_get_anomaly_results(
#     request: Request, # <-- Inject Request object to manually get header
#     username: str = Query(...),
#     role: str = Query(...)
#     # Removed token: str = Depends(oauth2_scheme) here
# ):
#     # Get Authorization header directly from the request
#     authorization_header = request.headers.get("Authorization")
#     if not authorization_header:
#         raise HTTPException(status_code=401, detail="Authorization header missing")

#     # Extract token string (remove "Bearer ")
#     if not authorization_header.startswith("Bearer "):
#         raise HTTPException(status_code=401, detail="Invalid Authorization header format. Must be 'Bearer <token>'")
#     token_string = authorization_header.replace("Bearer ", "")

#     if not token_string:
#         raise HTTPException(status_code=401, detail="Bearer token missing after 'Bearer ' prefix")

#     # Pass the raw token string to the service function
#     return await fetch_anomaly_results(username, role, token_string)

# NEW CALENDAR ENDPOINT
@app.get("/api/calendar/assignments/deadlines", response_model=List[Dict[str, Any]])
async def api_get_assignment_deadlines(
    student_id: Optional[str] = Query(None),
    class_id: Optional[str] = Query(None),
    subject_id: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    token: str = Depends(oauth2_scheme) # Assuming authentication is required
) -> List[Dict[str, Any]]:
    """
    API Gateway endpoint to fetch assignment deadlines from the Calendar microservice.
    """
    authorization = f"Bearer {token}"
    return await get_assignment_deadlines(
        student_id=student_id,
        class_id=class_id,
        subject_id=subject_id,
        start_date=start_date,
        end_date=end_date,
        authorization=authorization
    )


#non-academic
@app.get("/api/nonacademic/sports", response_model=list)
async def fetch_all_sports():
    return await get_all_sports()

@app.post("/api/nonacademic/sports", response_model=dict)
async def add_sport(sport: dict):
    return await create_sport(sport)

@app.get("/api/nonacademic/clubs", response_model=list)
async def fetch_all_clubs():
    return await get_all_clubs()

# Academic
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
    return await upload_assignment_file(student_id, assignment_id, file)

class StatusUpdateRequest(BaseModel):
    student_id: str

@app.post("/api/content/{content_id}")
async def mark_content_completed(content_id: str, payload: StatusUpdateRequest):
    return await mark_content_done(content_id, payload.student_id)

###teacher 

@app.get("/api/studentlist/{class_id}/{subject_id}")
async def get_student_list(class_id: str, subject_id: str):
    return await get_student_list_by_class_and_subject(class_id, subject_id)


@app.get("/api/submission/file/{submission_id}")
async def get_submission_file(submission_id: str):
    return await get_submission_file_by_id(submission_id)


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



class SubmissionResponse(BaseModel):
    submission_id: str
    subject_id: str
    subject_name: Optional[str] = None  
    content_file_path: str
    submit_time_date: datetime
    class_id: str
    class_name: Optional[str] = None
    file_name: str
    marks: Optional[int] = None
    assignment_id: str
    assignment_name: Optional[str] = None 
    student_id: str
    teacher_id: str

class CategorizedSubmissionsResponse(BaseModel):
    on_time_submissions: List[SubmissionResponse]
    late_submissions: List[SubmissionResponse]

@app.get("/api/submission_view/{teacher_id}", response_model=CategorizedSubmissionsResponse)
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

@app.get("/api/auto_graded_submissions/{teacher_id}",response_model=CategorizedSubmissionsResponse)
async def get_auto_graded_submissions(teacher_id: str):
    return await view_auto_graded_submissions_request(teacher_id)


@app.post("/api/review_auto_graded_marks/{teacher_id}")
async def review_marks(
    teacher_id: str,
    submission_id: str = Form(...),
    marks: float = Form(...),
    action: str = Form(...)
):
    return await review_auto_graded_marks_request(teacher_id, submission_id, marks, action)



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


# 1. Visualization endpoint
@app.get("/api/visualize_data/{subject_id}/{class_id}")
async def Visualize(subject_id: str, class_id: str):
   return await Visualize_data_list(subject_id, class_id)


class PredictionInput(BaseModel):
    SpecialEventThisWeek: int
    ResourcesUploadedThisWeek: int

# 2. Prediction endpoint (POST with JSON body)
@app.post("/api/predict_active_time/{subject_id}/{class_id}")
async def gateway_prediction_endpoint(
    subject_id: str,
    class_id: str,
    input_data: PredictionInput # Use the Pydantic model instead of Form data
):
    
    return await call_prediction_service(subject_id, class_id, input_data)
    


# 3. Train model
@app.post("/api/train/{subject_id}/{class_id}")
async def TrainModel(subject_id: str, class_id: str):
    return await model_train(subject_id, class_id)



@app.post("/api/update_collection/{subject_id}/{class_id}")
async def Update(subject_id: str, class_id: str):
    return await update_collection_active_time(subject_id, class_id)







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

@app.get("/api/dashboard/{student_id}/{class_id}/model-features")
async def dashboard_model_features(student_id: str, class_id: str):
    try:
        return await model_features(student_id, class_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/api/dashboard/{student_id}/{class_id}/model-feedback")
async def dashboard_model_feedback(student_id: str, class_id: str):
    try:
        return await get_model_feedback(student_id, class_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#Teacher Dashboard Routes
# @app.get("/api/teacher/dashboard/{teacher_id}/assignments")
# async def teacher_assignments(teacher_id: str):
#     try:
#         return await get_teacher_assignments(teacher_id)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/api/teacher/dashboard/{teacher_id}/assignments")
async def teacher_assignments(teacher_id: str):
    try:
        return await get_teacher_assignments(teacher_id)
    except httpx.HTTPStatusError as e:
        logging.error(f"Dashboard service error: {e.response.status_code} - {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        logging.error("Unexpected error: %s", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal server error")
    
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

@app.get("/api/teacher/dashboard/low-academic-attendance")
async def low_academic_attendance(threshold: float = 80.0):
    try:
        return await get_low_attendance_students(threshold)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
    
@app.get("/api/teacher/dashboard/low-attendance-count")
async def low_attendance_count():
    try:
        return await get_low_attendance_students_count()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
#Admin Dashboard Routes
@app.get("/api/admin/dashboard/users")
async def users(search_with_id: str = None, role: str = None, class_id: str = None):
    try:
        return await get_all_users(search_with_id, role, class_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/api/admin/dashboard/admin-access-profile")
async def admin_access_profile_endpoint(user_id: str = Query(...)):
    try:
        return await forward_admin_access_profile(user_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

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
app.include_router(attendanceRouter, prefix="/api")
    

