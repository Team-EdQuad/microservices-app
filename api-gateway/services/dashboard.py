import httpx
from fastapi import HTTPException
from fastapi.responses import JSONResponse


# DASHBOARD_SERVICE_URL = "http://127.0.0.1:8006"
DASHBOARD_SERVICE_URL = "http://dashboard:8000"


#---------------Student Dashboard Routes------------------
async def get_student_progress(student_id: str, class_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DASHBOARD_SERVICE_URL}/student/{student_id}/{class_id}/progress")
        response.raise_for_status()
        return response.json()

async def get_student_assignments(student_id: str, class_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DASHBOARD_SERVICE_URL}/student/{student_id}/{class_id}/assignments")
        response.raise_for_status()
        return response.json()
    
async def filter_assignments(student_id: str, class_id: str, status: str = None):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DASHBOARD_SERVICE_URL}/student/{student_id}/{class_id}/assignments/filterByStatus",
            params={"status": status}
        )
        response.raise_for_status()
        return response.json()

async def sort_assignments(student_id: str, class_id: str, status: str = None):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DASHBOARD_SERVICE_URL}/student/{student_id}/{class_id}/assignments/filterByDate",
            params={"status": status}
        )
        response.raise_for_status()
        return response.json()

async def get_student_attendance(student_id: str, class_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DASHBOARD_SERVICE_URL}/student/{student_id}/{class_id}/academicAttendanceRate")
        response.raise_for_status()
        return response.json()

async def get_student_exam_marks(student_id: str, class_id: str, exam_year: int = None):
    params = {"exam_year": exam_year} if exam_year else {}
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{DASHBOARD_SERVICE_URL}/student/{student_id}/{class_id}/exam-marks",
            params=params
        )
        response.raise_for_status()
        return response.json()
    
async def monthly_attendance(student_id: str, class_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DASHBOARD_SERVICE_URL}/student/{student_id}/{class_id}/mothlyAttendanceRate")
        response.raise_for_status()
        return response.json()

async def current_weekly_attendance(student_id: str, class_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DASHBOARD_SERVICE_URL}/student/{student_id}/{class_id}/weeklyAttendanceRate")
        response.raise_for_status()
        return response.json()
    
async def non_academic_attendance(student_id: str, class_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DASHBOARD_SERVICE_URL}/student/{student_id}/{class_id}/nonacademic-attendance")
        response.raise_for_status()
        return response.json()


async def engagement_score(student_id: str, class_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DASHBOARD_SERVICE_URL}/student/{student_id}/{class_id}/engagement-score")
        response.raise_for_status()
        return response.json()
    

async def model_features(student_id: str, class_id: str):
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{DASHBOARD_SERVICE_URL}/model-features/{student_id}/{class_id}/model-features")
        response.raise_for_status()
        return response.json()
    

async def get_model_feedback(student_id: str, class_id: str):
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{DASHBOARD_SERVICE_URL}/model-features/{student_id}/{class_id}/ai-feedback")
        response.raise_for_status()
        return response.json()


#-----------------End of Student Dashboard Routes------------------


#-----------------Teacher Dashboard Routes------------------
async def get_teacher_assignments(teacher_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DASHBOARD_SERVICE_URL}/teacher/{teacher_id}/assignments")
        response.raise_for_status()
        return response.json()

async def get_all_Classes():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DASHBOARD_SERVICE_URL}/teacher/classes")
        response.raise_for_status()
        return response.json()

async def get_exam_marks_teacher(class_id: str, exam_year: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DASHBOARD_SERVICE_URL}/teacher/{class_id}/{exam_year}/exam-marks")
        response.raise_for_status()
        return response.json()


async def get_student_progress_teacher(class_id: str, year:int =None):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DASHBOARD_SERVICE_URL}/teacher/{class_id}/student_progress",
        params={"year": year}
        )
        response.raise_for_status()
        return response.json()

async def get_weekly_attendance(class_id: str, year: int, week_num: int):
    async with httpx.AsyncClient() as client:
        # Pass query parameters in the URL
        response = await client.get(
            f"{DASHBOARD_SERVICE_URL}/teacher/weekly_attendance",
            params={"class_id": class_id, "year": year, "week_num": week_num}
        )
        response.raise_for_status()
        return response.json()
#-----------------End of Teacher Dashboard Routes------------------

#-----------------Admin Dashboard Routes------------------
async def get_all_users(search_with_id: str = None, role: str = None, class_id: str = None):
    params = {}
    if search_with_id:
        params["search_with_id"] = search_with_id
    if role:
        params["role"] = role
    if class_id:
        params["class_id"] = class_id

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DASHBOARD_SERVICE_URL}/admin/user_data", params=params)
        response.raise_for_status()
        return response.json()

async def get_stats():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DASHBOARD_SERVICE_URL}/admin/stats")
        response.raise_for_status()
        return response.json()
    
async def get_exam_marks_admin(class_id: str, exam_year: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DASHBOARD_SERVICE_URL}/admin/{class_id}/{exam_year}/exam-marks")
        response.raise_for_status()
        return response.json()


async def get_student_progress_admin(class_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DASHBOARD_SERVICE_URL}/admin/{class_id}/student_progress")
        response.raise_for_status()
        return response.json()

async def get_weekly_attendance_admin(class_id: str, year: int, week_num: int):
    async with httpx.AsyncClient() as client:
        # Pass query parameters in the URL
        response = await client.get(
            f"{DASHBOARD_SERVICE_URL}/admin/weekly_attendance",
            params={"class_id": class_id, "year": year, "week_num": week_num}
        )
        response.raise_for_status()
        return response.json()
#-----------------End of Admin Dashboard Routes------------------