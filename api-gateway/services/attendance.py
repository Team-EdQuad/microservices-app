import httpx
from fastapi import APIRouter, Form, File, UploadFile, Query
from datetime import datetime
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict

ATTENDANCE_SERVICE_URL = "http://127.0.0.1:8004"

attendanceRouter = APIRouter(
    tags=["Attendance Service"],
    # prefix="/attendance"
)

class StudentsOfClassRequest(BaseModel):
    class_id: str
    subject_type: str
    subject_id: str
    date: str = None  # Optional

class AttendanceEntry(BaseModel):
    class_id: str
    subject_id: str
    date: str
    status: Dict[str, str]  # e.g., {"std001": "present", "std002": "absent"}

# get class students
@attendanceRouter.post("/attendance/students/by-class")
async def forward_get_class_students(request_data: StudentsOfClassRequest):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{ATTENDANCE_SERVICE_URL}/attendance/students/by-class",
                json=request_data.dict()
            )
        return JSONResponse(content=response.json(), status_code=response.status_code)

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Gateway error: {str(e)}"}
        )
    
# mark attendance
@attendanceRouter.post("/attendance/attendance_marking", status_code=201)
async def forward_mark_attendance(request_data: AttendanceEntry):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{ATTENDANCE_SERVICE_URL}/attendance/attendance_marking",
                json=request_data.dict()
            )
        return JSONResponse(content=response.json(), status_code=response.status_code)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Gateway error: {str(e)}"}
        )

# update attendance
@attendanceRouter.put("/attendance/update_attendance_of_class/{attendance_id}", status_code=202)
async def forward_update_attendance(attendance_id: str, updated_attendance: AttendanceEntry):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{ATTENDANCE_SERVICE_URL}/attendance/update_attendance_of_class/{attendance_id}",
                json=updated_attendance.dict()
            )
        return JSONResponse(content=response.json(), status_code=response.status_code)

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Gateway error: {str(e)}"}
        )

# delete attendance
@attendanceRouter.delete("/attendance/delete-attendance-of-class/{attendance_id}", status_code=200)
async def forward_delete_attendance(attendance_id: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{ATTENDANCE_SERVICE_URL}/attendance/delete-attendance-of-class/{attendance_id}"
            )
        return JSONResponse(content=response.json(), status_code=response.status_code)

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Gateway error: {str(e)}"}
        )

# class acadamic attendance ratio
@attendanceRouter.get("/attendance/class/academic/ratio", status_code=200)
async def forward_class_academic_ratio(class_id: str, subject_id: str = "academic", summary_type: str = "monthly"):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{ATTENDANCE_SERVICE_URL}/attendance/class/academic/ratio",
                params={"class_id": class_id, "subject_id": subject_id, "summary_type": summary_type}
            )
        return JSONResponse(content=response.json(), status_code=response.status_code)
    except Exception as e:
        return JSONResponse(
            status_code=500, 
            content={"detail": f"Gateway error: {str(e)}"}
        )

# class nonacadamic attendance ratio
@attendanceRouter.get("/attendance/class/nonacademic/ratio", status_code=200)
async def forward_class_nonacademic_ratio(class_id: str, subject_id: str, summary_type: str = "monthly"):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{ATTENDANCE_SERVICE_URL}/attendance/class/nonacademic/ratio",
                params={"class_id": class_id, "subject_id": subject_id, "summary_type": summary_type}
            )
        return JSONResponse(content=response.json(), status_code=response.status_code)
    except Exception as e:
        return JSONResponse(
            status_code=500, 
            content={"detail": f"Gateway error: {str(e)}"}
        )

# students acadamic attendance ratio
@attendanceRouter.get("/attendance/student/academic/ratio", status_code=200)
async def forward_student_academic_ratio(student_id: str, subject_id: str = "academic", summary_type: str = "monthly"):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{ATTENDANCE_SERVICE_URL}/attendance/student/academic/ratio",
                params={"student_id": student_id, "subject_id": subject_id, "summary_type": summary_type}
            )
        return JSONResponse(content=response.json(), status_code=response.status_code)
    except Exception as e:
        return JSONResponse(
            status_code=500, 
            content={"detail": f"Gateway error: {str(e)}"}
        )

# students acadamic attendance ratio
@attendanceRouter.get("/attendance/student/nonacademic/ratio", status_code=200)
async def forward_student_nonacademic_ratio(student_id: str, subject_id: str, summary_type: str = "monthly"):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{ATTENDANCE_SERVICE_URL}/attendance/student/nonacademic/ratio",
                params={"student_id": student_id, "subject_id": subject_id, "summary_type": summary_type}
            )
        return JSONResponse(content=response.json(), status_code=response.status_code)
    except Exception as e:
        return JSONResponse(
            status_code=500, 
            content={"detail": f"Gateway error: {str(e)}"}
        )

# class acadamic attendance summary
@attendanceRouter.get("/attendance/class/academic/summary", status_code=200)
async def forward_class_academic_summary(
    class_id: str,
    subject_id: str = "academic",
    summary_type: str = "monthly",
    month: str = None
):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{ATTENDANCE_SERVICE_URL}/attendance/class/academic/summary",
                params={"class_id": class_id, "subject_id": subject_id, "summary_type": summary_type, "month": month}
            )
        return JSONResponse(content=response.json(), status_code=response.status_code)
    except Exception as e:
        return JSONResponse(
            status_code=500, 
            content={"detail": f"Gateway error: {str(e)}"}
        )

# class nonacadamic attendance summary
@attendanceRouter.get("/attendance/class/nonacademic/summary", status_code=200)
async def forward_class_nonacademic_summary(
    class_id: str,
    subject_id: str,
    summary_type: str = "monthly",
    month: str = None
):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{ATTENDANCE_SERVICE_URL}/attendance/class/nonacademic/summary",
                params={"class_id": class_id, "subject_id": subject_id, "summary_type": summary_type, "month": month}
            )
        return JSONResponse(content=response.json(), status_code=response.status_code)
    except Exception as e:
        return JSONResponse(
            status_code=500, 
            content={"detail": f"Gateway error: {str(e)}"}
        )

# students acadamic attendance summary
@attendanceRouter.get("/attendance/student/academic/summary", status_code=200)
async def forward_student_academic_summary(
    student_id: str,
    subject_id: str = "academic",
    summary_type: str = "monthly",
    month: str = None
):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{ATTENDANCE_SERVICE_URL}/attendance/student/academic/summary",
                params={"student_id": student_id, "subject_id": subject_id, "summary_type": summary_type, "month": month}
            )
        return JSONResponse(content=response.json(), status_code=response.status_code)
    except Exception as e:
        return JSONResponse(
            status_code=500, 
            content={"detail": f"Gateway error: {str(e)}"}
        )

# students nonacadamic attendance summary
@attendanceRouter.get("/attendance/student/nonacademic/summary", status_code=200)
async def forward_student_nonacademic_summary(
    student_id: str,
    subject_id: str,
    summary_type: str = "monthly",
    month: str = None
):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{ATTENDANCE_SERVICE_URL}/attendance/student/nonacademic/summary",
                params={"student_id": student_id, "subject_id": subject_id, "summary_type": summary_type, "month": month}
            )
        return JSONResponse(content=response.json(), status_code=response.status_code)
    except Exception as e:
        return JSONResponse(
            status_code=500, 
            content={"detail": f"Gateway error: {str(e)}"}
        )

# class history
@attendanceRouter.get("/attendance/history", status_code=200)
async def forward_class_history(
    class_id: str,
    subject_id: str,
    date: str
):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{ATTENDANCE_SERVICE_URL}/attendance/history",
                params={"class_id": class_id, "subject_id": subject_id, "date": date}
            )
        return JSONResponse(content=response.json(), status_code=response.status_code)
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Gateway error: {str(e)}"})

# document upload   
@attendanceRouter.post("/attendance/document-upload", status_code=201)
async def forward_medical_upload(
    file: UploadFile = File(...),
    student_id: str = Form(...),
    class_id: str = Form(...),
    subject_id: str = Form("academic"),
    date: str = Form(datetime.now().strftime("%Y-%m-%d"))
):
    try:
        file_bytes = await file.read()

        files = {
            "file": (file.filename, file_bytes, file.content_type),
        }
        data = {
            "student_id": student_id,
            "class_id": class_id,
            "subject_id": subject_id,
            "date": date
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{ATTENDANCE_SERVICE_URL}/attendance/document-upload",
                files=files,
                data=data
            )
        return JSONResponse(content=response.json(), status_code=response.status_code)

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Gateway error: {str(e)}"}
        )

# document fetch
@attendanceRouter.get("/attendance/documents", status_code=200)
async def forward_get_medicals(
    class_id: str = Query("all"),
    subject_id: str = Query("all"),
    student_id: str = Query("all")
):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{ATTENDANCE_SERVICE_URL}/attendance/documents",
                params={
                    "class_id": class_id,
                    "subject_id": subject_id,
                    "student_id": student_id
                }
            )
        return JSONResponse(content=response.json(), status_code=response.status_code)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Gateway error: {str(e)}"}
        )
    
# delete document
@attendanceRouter.delete("/attendance/delete/document/{document_id}", status_code=200)
async def forward_delete_medical_document(document_id: str):
    """
    API Gateway: Forwards DELETE request to attendance service's document deletion route.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{ATTENDANCE_SERVICE_URL}/attendance/delete/document/{document_id}"
            )
        return JSONResponse(content=response.json(), status_code=response.status_code)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Gateway error: {str(e)}"}
        )
    
# get student non-acadamic subjecta
@attendanceRouter.get("/attendance/non-acadamic/subjects/{student_id}", summary="Forward student-specific non-academic subjects")
async def forward_get_student_nonacadamic_subjects(student_id: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{ATTENDANCE_SERVICE_URL}/attendance/non-acadamic/subjects/{student_id}"
            )
        return JSONResponse(content=response.json(), status_code=response.status_code)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Gateway error: {str(e)}"}
        )

# get all non-acadamic subjects
@attendanceRouter.get("/attendance/non-acadamic/subjects", summary="Forward all non-academic subjects")
async def forward_get_all_nonacadamic_subjects():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{ATTENDANCE_SERVICE_URL}/attendance/non-acadamic/subjects"
            )
        return JSONResponse(content=response.json(), status_code=response.status_code)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Gateway error: {str(e)}"}
        )

# get attendance prediction
@attendanceRouter.get("/attendance/summary", summary="Forward attendance prediction request")
async def forward_get_attendance_prediction(
    class_id: str = Query("all"),
    subject_id: str = Query("all"),
    start_date: str = Query("2023-01-01"),
    end_date: str = Query("2023-01-30"),
    current_date: str = Query(datetime.now().strftime("%Y-%m-%d"))
):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{ATTENDANCE_SERVICE_URL}/attendance/summary",
                params={
                    "class_id": class_id,
                    "subject_id": subject_id,
                    "start_date": start_date,
                    "end_date": end_date,
                    "current_date": current_date,
                }
            )
        return JSONResponse(content=response.json(), status_code=response.status_code)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Gateway error: {str(e)}"}
        )
