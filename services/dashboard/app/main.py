from fastapi import FastAPI
from .services.studentdashboard import router as item_router
from .services.student_dashboard import student_dashboard_router
from .services.teacher_dashboard import teacher_dashboard_router
from .services.admin_dashboard import admin_dashboard_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Dashboard Management API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(item_router, prefix="/item", tags=["nonacademic"])
app.include_router(student_dashboard_router, prefix="/student", tags=["student_dashboard"])
app.include_router(teacher_dashboard_router, prefix = "/teacher", tags=["teacher_dashboard"])
app.include_router(admin_dashboard_router, prefix = "/admin", tags=["admin_dashboard"])
