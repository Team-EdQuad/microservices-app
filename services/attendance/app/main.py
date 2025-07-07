from fastapi import FastAPI
import asyncio
from contextlib import asynccontextmanager
# from app.services.background_services.attendance_tracker import attendance_tracker
from app.utils.mongodb_connection import attendance_store
# from app.services.background_services.scheduler import setup_scheduler, start_scheduler
from fastapi.middleware.cors import CORSMiddleware

from app.api.get_class_students_router import router as get_class_students_router
from app.api.mark_class_attendance_router import router as mark_class_attendance_router
from app.api.update_class_attendance_router import router as update_class_attendance_router
from app.api.delete_class_attendance_router import router as delete_class_attendance_router
from app.api.get_attendance_ratio_router import classrouter as class_ratio_router
from app.api.get_attendance_ratio_router import studentrouter as student_ratio_router
from app.api.get_attendance_summary_router import classrouter as class_summary_router
from app.api.get_attendance_summary_router import studentrouter as student_summary_router
from app.api.get_class_history_router import router as get_class_history_router
from app.api.medical_upload_router import router as medical_upload_router
from app.api.get_medicals_router import router as get_medicals_router
from app.api.medical_delete_router import router as medical_delete_router
from app.api.get_nonacadamic_subjects_router import studentrouter as get_student_nonacadamic_subjects_router
from app.api.get_nonacadamic_subjects_router import allrouter as get_all_nonacadamic_subjects_router
from app.api.attendance_prediction_router import router as prediction_router
from app.api.store_calendar_event_router import router as calendar_event_router
from app.api.get_daily_attendance_router import router as daily_attendance_router

from app.services.dashboard_services.get_monthly_summary import router as monthly_summary_router
from app.services.dashboard_services.get_weekly_summary import router as weekly_summary_router
from app.services.dashboard_services.get_daily_summary import router as daily_summary_router

# from .ml.routes import router as ml_router         # this is for model training and prediction 

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     asyncio.create_task(attendance_tracker(attendance_store))
    
#     setup_scheduler()
#     start_scheduler()

#     yield
    

app = FastAPI(title="Attendance Management API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(get_class_students_router)
app.include_router(mark_class_attendance_router)
app.include_router(update_class_attendance_router)
app.include_router(delete_class_attendance_router)
app.include_router(class_ratio_router)
app.include_router(student_ratio_router)
app.include_router(class_summary_router)
app.include_router(student_summary_router)
app.include_router(get_class_history_router)
app.include_router(medical_upload_router)
app.include_router(get_medicals_router)
app.include_router(medical_delete_router)
app.include_router(get_student_nonacadamic_subjects_router)
app.include_router(get_all_nonacadamic_subjects_router)
app.include_router(prediction_router)
app.include_router(calendar_event_router)
app.include_router(daily_attendance_router)

app.include_router(monthly_summary_router)
app.include_router(weekly_summary_router)
app.include_router(daily_summary_router)

# app.include_router(ml_router, prefix="/ml", tags=["Machine Learning"])


