from fastapi import FastAPI, HTTPException, APIRouter, Body
from services.nonacademic import get_all_sports, create_sport, get_all_clubs, create_club, filter_sports
from services.dashboard import get_student_progress, get_student_assignments,filter_assignments,sort_assignments, get_student_attendance,get_student_exam_marks,monthly_attendance, current_weekly_attendance,non_academic_attendance,engagement_score
from services.dashboard import get_teacher_assignments, get_exam_marks, get_student_progress_teacher, get_weekly_attendance,get_all_Classes
from services.dashboard import get_exam_marks_admin,  get_student_progress_admin, get_weekly_attendance_admin, get_stats, get_all_users

from services import usermanagement


from schemas.usermanagement import LoginRequest
import httpx 
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta

from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="Microservices API Gateway") 

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Non-Academic Routes
# User-management
@app.post("/api/user-management/login")
async def login_user(credentials: LoginRequest):
    return await usermanagement.login_user(credentials.dict())

#non-academic
@app.get("/api/nonacademic/sports", response_model=list)
async def fetch_all_sports():
    return await get_all_sports()

@app.post("/api/nonacademic/sports", response_model=dict)
async def add_sport(sport: dict):
    return await create_sport(sport)

@app.get("/api/nonacademic/sports/filter", response_model=list)
async def filter_sports_endpoint(type: str = None, category: str = None):
    return await filter_sports(type, category)

@app.get("/api/nonacademic/clubs", response_model=list)
async def fetch_all_clubs():
    return await get_all_clubs()

@app.post("/api/nonacademic/clubs", response_model=dict)
async def add_club(club: dict):
    return await create_club(club)


TEST_SERVICE_URL = "http://127.0.0.1:8006" 
@app.get("/item/nonacademic/{item_id}")
async def get_nonacademic_item(item_id: int):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{TEST_SERVICE_URL}/item/nonacademic/{item_id}")
            response.raise_for_status() 
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error fetching item {item_id}: {str(exc)}")
    
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
        return await get_exam_marks(class_id, exam_year)
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

    




    

