import sys
import os


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'services')))


from fastapi import FastAPI, HTTPException, UploadFile, File, Form
#from services.nonacademic import get_all_sports, create_sport, get_all_clubs, create_club, filter_sports

import httpx 
from fastapi.responses import JSONResponse
from typing import List, Optional
from services.academic import create_assignment_request,upload_content_request,view_ungraded_manual_submissions,update_manual_marks,add_exam_marks_request,get_subject_names,get_student_content,get_all_assignments,get_assignment_by_id,get_assignment_marks,get_exam_marks, upload_assignment_file ,mark_content_done,get_subject_and_class_for_teacher
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
    deadline: str = Form(...),
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
    student_id: str = Form(...),
    subject_id: str = Form(...),
    exam_type: str = Form(...),
    marks: float = Form(...)
):
    form_data = {
        "student_id": student_id,
        "subject_id": subject_id,
        "exam_type": exam_type,
        "marks": marks
    }
    return await add_exam_marks_request(form_data)
