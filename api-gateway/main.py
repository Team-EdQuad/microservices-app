import sys
import os


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'services')))


from fastapi import FastAPI, HTTPException, UploadFile, File
#from services.nonacademic import get_all_sports, create_sport, get_all_clubs, create_club, filter_sports

import httpx 
from fastapi.responses import JSONResponse
from typing import List
from services.academic import get_subject_names,get_student_content,get_all_assignments,get_assignment_by_id,get_assignment_marks,get_exam_marks, upload_assignment_file ,mark_content_done

app = FastAPI(title="Microservices API Gateway") 

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
    marks = await get_assignment_marks(student_id)
    if not marks:
        return []  # or raise HTTPException(status_code=404, detail="No marks found")
    return marks

@app.get("/api/exammarks/{student_id}")
async def fetch_exam_marks(student_id: str):
    marks = await get_exam_marks(student_id)
    if not marks:
        return []
    return marks

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
