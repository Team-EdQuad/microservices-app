from fastapi import FastAPI, HTTPException
from services.nonacademic import get_all_sports, create_sport, get_all_clubs, create_club, filter_sports
from services.dashboard import get_student_progress, get_student_assignments, get_student_attendance, get_student_non_academic
from services.dashboard import get_teacher_assignments, get_exam_marks, get_student_progress_teacher, get_weekly_attendance
from services.dashboard import get_exam_marks_admin,  get_student_progress_admin, get_weekly_attendance_admin, get_stats, get_all_users

import httpx 
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta

app = FastAPI(title="Microservices API Gateway") 

#Non-Academic Routes
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

# NON_ACADEMIC_SERVICE_URL = "http://127.0.0.1:8003" 
# @app.get("/item/nonacademic/{item_id}")
# async def get_nonacademic_item(item_id: int):
#     try:
#         async with httpx.AsyncClient() as client:
#             # Add trailing slash if the Non-Academic service requires it
#             response = await client.get(f"{NON_ACADEMIC_SERVICE_URL}/item/nonacademic/{item_id}")
#             response.raise_for_status()  # Ensure HTTP errors are raised
#             return response.json()
#     except httpx.HTTPStatusError as exc:
#         raise HTTPException(status_code=exc.response.status_code, detail=str(exc))
#     except Exception as exc:
#         raise HTTPException(status_code=500, detail=f"Error fetching item {item_id}: {str(exc)}")


#Test
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

@app.get("/api/dashboard/{student_id}/{class_id}/attendance")
async def dashboard_attendance(student_id: str, class_id: str):
    try:
        return await get_student_attendance(student_id, class_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/{student_id}/{class_id}/non-academic")
async def dashboard_non_academic(student_id: str, class_id: str):
    try:
        return await get_student_non_academic(student_id, class_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

#Teacher Dashboard Routes
@app.get("/api/teacher/dashboard/{teacher_id}/assignments")
async def teacher_assignments(teacher_id: str):
    try:
        return await get_teacher_assignments(teacher_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/teacher/dashboard/{class_id}/{exam_year}/exam-marks")
async def exam_marks(class_id: str, exam_year: int):
    try:
        return await get_exam_marks(class_id, exam_year)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/api/teacher/dashboard/{class_id}/progress")
async def student_progress_teacher(class_id: str):
    try:
        return await get_student_progress_teacher(class_id)
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

    




    

