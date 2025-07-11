from datetime import datetime
import uuid
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from typing import List
from openai import BaseModel
from ..models.academic import StudentResponse,AssignmentResponse, ClassResponse, ContentUploadResponse, StudentsResponse,SubjectClassResponse, SubjectResponse, SubjectWithClasses,SubmissionResponse
from .database import db
from .google_drive import get_drive_service, FOLDER_IDS
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
import io
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
import os
import aiofiles
from fastapi.responses import FileResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
ALLOWED_EXTENSIONS = {"pdf", "txt", "mp3", "mp4"}  # Allowed file types
UPLOAD_DIR = "local_uploads"


router = APIRouter()

@router.get("/submission/file/{submission_id}")
async def get_submission_file(submission_id: str):
    try:
        # Find the submission in either collection
        submission = db["submission"].find_one({"submission_id": submission_id})
        if not submission:
            submission = db["grading_submissions"].find_one({"submission_id": submission_id})
        
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        # Get the LOCAL file path from the record
        file_path = submission.get("content_file_path")
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found on the server for this submission.")
        
        file_name = os.path.basename(file_path)
        
        # Return file from local path using FileResponse
        return FileResponse(
            path=file_path,
            filename=file_name,
            media_type='application/octet-stream', # Browser will handle based on extension
            headers={"Content-Disposition": f"inline; filename=\"{file_name}\""}
        )
        
    except Exception as e:
        logger.error(f"Error retrieving file for submission {submission_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve file: {str(e)}")


#view accessible subject and class  ( teacher )
@router.get("/subjectNclass/{teacher_id}", response_model=SubjectClassResponse)
async def get_subjectNclass(teacher_id: str):
    teacher = db["teacher"].find_one({"teacher_id": teacher_id})

    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    subjects_classes_data = teacher.get("subjects_classes", [])
    if not subjects_classes_data:
        raise HTTPException(status_code=404, detail="No subject-class mapping found")

    # Collect all unique subject_ids and class_ids
    subject_ids = {sc["subject_id"] for sc in subjects_classes_data}
    class_ids = {cls_id for sc in subjects_classes_data for cls_id in sc.get("class_id", [])}

    # Fetch subject documents
    subject_docs = {
        s["subject_id"]: s["subject_name"]
        for s in db["subject"].find({"subject_id": {"$in": list(subject_ids)}}, {"_id": 0})
    }

    # Fetch class documents
    class_docs = {
        c["class_id"]: c["class_name"]
        for c in db["class"].find({"class_id": {"$in": list(class_ids)}}, {"_id": 0})
    }

    # Build the response
    result = []
    for sc in subjects_classes_data:
        subject_id = sc["subject_id"]
        subject_name = subject_docs.get(subject_id, "Unknown Subject")

        class_list = [
            ClassResponse(
                class_id=cid,
                class_name=class_docs.get(cid, "Unknown Class")
            )
            for cid in sc.get("class_id", [])
        ]

        result.append(SubjectWithClasses(
            subject_id=subject_id,
            subject_name=subject_name,
            classes=class_list
        ))

    return SubjectClassResponse(subjects_classes=result)


#assignment create
@router.post("/assignmentcreate/{class_id}/{subject_id}/{teacher_id}", response_model=AssignmentResponse)
async def create_assignment(
    class_id: str,
    subject_id: str,
    teacher_id: str,
    assignment_name: str = Form(...),
    description: str = Form(...),
    deadline: str = Form(...),
    grading_type: str = Form(...),
    sample_answer: str = Form(None),
    file: UploadFile = File(...)
):
    if grading_type == "auto" and not sample_answer:
        raise HTTPException(status_code=400, detail="Sample answer is required for auto grading.")

    assignment_id = f"ASM{uuid.uuid4().hex[:6].upper()}"

    # Define the local file path
    assignments_path = os.path.join(UPLOAD_DIR, "assignments")
    os.makedirs(assignments_path, exist_ok=True)  # Create directory if it doesn't exist
    
    file_extension = file.filename.split('.')[-1]
    file_path = os.path.join(assignments_path, f"{assignment_id}.{file_extension}")

    try:
        # Save the file locally asynchronously
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
  
        try:
            deadline_dt = datetime.fromisoformat(deadline)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid deadline format. Use ISO format.")

        assignment_data = {
            "assignment_id": assignment_id,
            "assignment_name": assignment_name,
            "description": description,
            "deadline": deadline_dt,
            "assignment_file_path": file_path,  # Store the local file path
            "class_id": class_id,
            "subject_id": subject_id,
            "teacher_id": teacher_id,
            "grading_type": grading_type,
            "sample_answer": sample_answer if grading_type == "auto" else None,
            "created_at": datetime.utcnow()
        }

        db["assignment"].insert_one(assignment_data)
        
        # You may need to adjust your AssignmentResponse model to expect 'assignment_file_path'
        return assignment_data

    except Exception as e:
        logger.error(f"[ERROR] Creating assignment_id={assignment_id} -> {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create assignment: {str(e)}")


#upload content
@router.post("/contentupload/{class_id}/{subject_id}", response_model=ContentUploadResponse)
async def upload_content(
    class_id: str,
    subject_id: str,
    file: UploadFile = File(...),
    content_name: str = Form(...),
    description: str = Form(...),
):
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only PDF, TXT, MP3, and MP4 files are allowed.")

    content_id = f"CNT{uuid.uuid4().hex[:3].upper()}"
    
    # Define the local file path
    content_path = os.path.join(UPLOAD_DIR, "content")
    os.makedirs(content_path, exist_ok=True) # Create directory if it doesn't exist
    
    file_path = os.path.join(content_path, f"{content_id}_{file.filename}")

    try:
        # Save the file locally asynchronously
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)

        content_data = {
            "content_id": content_id,
            "content_name": content_name,
            "content_file_path": file_path, # Store the local file path
            "upload_date": datetime.now().strftime("%Y-%m-%d"),
            "description": description,
            "class_id": class_id,
            "subject_id": subject_id
        }

        db["content"].insert_one(content_data)
        
        # Adjust your ContentUploadResponse model to expect 'content_file_path'
        return ContentUploadResponse(**content_data)

    except Exception as e:
        logger.error(f"[ERROR] Uploading content_id={content_id} -> {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to upload content: {str(e)}")
    


class CategorizedSubmissionsResponse(BaseModel):
    on_time_submissions: List[SubmissionResponse]
    late_submissions: List[SubmissionResponse]

@router.get("/submission_view/{teacher_id}", response_model=CategorizedSubmissionsResponse)
async def view_manual_submission(teacher_id: str):
    teacher_data = db["teacher"].find_one({"teacher_id": teacher_id})
    if not teacher_data:
        raise HTTPException(status_code=404, detail="Teacher not found")

    subjects_classes = teacher_data.get("subjects_classes", [])
    if not subjects_classes:
        raise HTTPException(status_code=404, detail="No subjects or classes found for this teacher")

    filters = []
    for item in subjects_classes:
        subject_id = item.get("subject_id")
        class_ids = item.get("class_id", [])
        for cls_id in class_ids:
            filters.append({
                "teacher_id": teacher_id,
                "subject_id": subject_id,
                "class_id": cls_id,
                "$or": [
                    {"marks": None},
                    {"marks": {"$exists": False}}
                ]
            })

    on_time = []
    late = []

    for f in filters:
        submissions_cursor = db["submission"].find(f)
        for submission in submissions_cursor:
            assignment = db["assignment"].find_one(
                {"assignment_id": submission["assignment_id"]},
                {"assignment_name": 1, "deadline": 1, "_id": 0}
            )

            submission["assignment_name"] = assignment.get("assignment_name") if assignment else None
            deadline = assignment.get("deadline") if assignment else None

            # Add class_name and subject_name
            class_doc = db["class"].find_one(
                {"class_id": submission["class_id"]}, {"class_name": 1, "_id": 0}
            )
            subject_doc = db["subject"].find_one(
                {"subject_id": submission["subject_id"]}, {"subject_name": 1, "_id": 0}
            )

            submission["class_name"] = class_doc.get("class_name") if class_doc else None
            submission["subject_name"] = subject_doc.get("subject_name") if subject_doc else None

            # Convert submit_time and deadline to datetime
            submit_time = submission.get("submit_time_date")
            if isinstance(submit_time, str):
                submit_time = datetime.fromisoformat(submit_time)

            if isinstance(deadline, str):
                deadline = datetime.fromisoformat(deadline)

            response = SubmissionResponse(**submission)

            if deadline and submit_time and submit_time > deadline:
                late.append(response)
            else:
                on_time.append(response)

    if not on_time and not late:
        raise HTTPException(status_code=404, detail="No submissions found")

    return CategorizedSubmissionsResponse(
        on_time_submissions=on_time,
        late_submissions=late
    )

@router.post("/update_submission_marks/{teacher_id}", response_model=SubmissionResponse)
async def update_submission_marks(
    teacher_id: str,
    submission_id: str = Form(...),
    marks: float = Form(...),
):
    # Validate marks
    if marks < 0 or marks > 100:
        raise HTTPException(status_code=400, detail="Marks must be between 0 and 100.")

    # Fetch the ungraded submission and ensure it's assigned to the teacher
    submission = db["submission"].find_one({
        "submission_id": submission_id,
        "teacher_id": teacher_id,
        "marks": None  # Ensure it hasn't been graded yet
    })

    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found or already graded")

    # Update the marks
    try:
        db["submission"].update_one(
            {"submission_id": submission_id},
            {"$set": {"marks": marks}}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update marks: {str(e)}")

    # Return the updated submission
    updated_submission = db["submission"].find_one({"submission_id": submission_id})
    return SubmissionResponse(**updated_submission)


@router.post("/update_exam_marks", response_model=dict)
async def add_exam_marks(
    teacher_id: str = Form(...),
    student_id: str = Form(...),
    exam_year: int = Form(...),
    subject_name: str = Form(...),
    term: int = Form(...),
    marks: float = Form(...),
):
    # Validate term (must be 1, 2, or 3)
    if term not in [1, 2, 3]:
        raise HTTPException(status_code=400, detail="Term must be 1, 2, or 3.")

    # Fetch teacher data to validate permissions
    teacher = db["teacher"].find_one({"teacher_id": teacher_id})
    if not teacher:
        raise HTTPException(status_code=404, detail=f"Teacher with ID {teacher_id} not found.")
    
    # Fetch subject data to get subject_id
    subject = db["subject"].find_one({"subject_name": subject_name})
    if not subject:
        raise HTTPException(status_code=404, detail=f"Subject '{subject_name}' not found.")
    subject_id = subject["subject_id"]

    # Fetch student data to get class_id and validate subject enrollment
    student = db["student"].find_one({"student_id": student_id})
    if not student:
        raise HTTPException(status_code=404, detail=f"Student with ID {student_id} not found.")
    class_id = student["class_id"]
    if subject_id not in student["subject_id"]:
        raise HTTPException(status_code=400, detail=f"Student {student_id} is not enrolled in {subject_name}.")

    # Validate teacher's permission for subject and class
    subjects_classes = teacher["subjects_classes"]
    teacher_subject = next((sc for sc in subjects_classes if sc["subject_id"] == subject_id), None)
    if not teacher_subject:
        raise HTTPException(status_code=403, detail=f"Teacher {teacher_id} is not assigned to {subject_name}.")
    if class_id not in teacher_subject["class_id"]:
        raise HTTPException(status_code=403, detail=f"Teacher {teacher_id} is not assigned to class {class_id} for {subject_name}.")

    # Generate a unique exam_id
    exam_id = f"EXM{uuid.uuid4().hex[:6].upper()}"

    # Check for existing exam marks record
    existing_record = db["exam_marks"].find_one({"student_id": student_id, "exam_year": exam_year})

    if existing_record:
        # Find or create the subject entry in exam_marks
        subject_found = False
        for subject_exam in existing_record["exam_marks"]:
            if subject_exam["subject_id"] == subject_id:
                subject_found = True
                # Check if term already exists
                if any(exam["term"] == term for exam in subject_exam["exams"]):
                    raise HTTPException(status_code=400, detail=f"Marks for Term {term} in {subject_name} already exist for {exam_year}.")
                # Append new exam data
                subject_exam["exams"].append({
                    "exam_id": exam_id,
                    "term": term,
                    "marks": marks,
                })
                break

        if not subject_found:
            existing_record["exam_marks"].append({
                "subject_id": subject_id,
                "subject_name": subject_name,
                "exams": [{"exam_id": exam_id, "term": term, "marks": marks}]
            })

        # Update the record in the database
        db["exam_marks"].update_one(
            {"student_id": student_id, "exam_year": exam_year},
            {"$set": {"exam_marks": existing_record["exam_marks"]}}
        )
        message = f"Marks updated for student {student_id} in {subject_name}, Term {term}, {exam_year}."
    else:
        # Create a new exam marks record
        exam_marks_data = {
            "student_id": student_id,
            "exam_year": exam_year,
            "class_id": class_id,
            "teacher_id": teacher_id,
            "exam_marks": [{
                "subject_id": subject_id,
                "subject_name": subject_name,
                "exams": [{"exam_id": exam_id, "term": term, "marks": marks}]
            }]
        }
        db["exam_marks"].insert_one(exam_marks_data)
        message = f"New marks record created for student {student_id} in {subject_name}, Term {term}, {exam_year}."

    return {"detail": message, "exam_id": exam_id}


@router.get("/students/{class_id}/{subject_id}", response_model=StudentsResponse)
async def get_students_by_class_and_subject(class_id: str, subject_id: str):
    # Fetch students in the specified class who are enrolled in the subject
    students = db["student"].find(
        {
            "class_id": class_id,
            "subject_id": subject_id
        },
        {"_id": 0, "student_id": 1, "full_name": 1}
    )

    student_list = [
        StudentResponse(student_id=student["student_id"], full_name=student["full_name"])
        for student in students
    ]

    if not student_list:
        raise HTTPException(status_code=404, detail=f"No students found for class {class_id} and subject {subject_id}")

    return StudentsResponse(students=student_list)



@router.get("/auto_graded_submissions/{teacher_id}", response_model=CategorizedSubmissionsResponse)
async def view_auto_graded_submissions(teacher_id: str):
    teacher_data = db["teacher"].find_one({"teacher_id": teacher_id})
    if not teacher_data:
        raise HTTPException(status_code=404, detail="Teacher not found")

    subjects_classes = teacher_data.get("subjects_classes", [])
    if not subjects_classes:
        raise HTTPException(status_code=404, detail="No subjects or classes found for this teacher")

    filters = []
    for item in subjects_classes:
        subject_id = item.get("subject_id")
        class_ids = item.get("class_id", [])
        for cls_id in class_ids:
            filters.append({
                "teacher_id": teacher_id,
                "subject_id": subject_id,
                "class_id": cls_id,
                "grading_type": "auto"
            })

    on_time = []
    late = []

    for f in filters:
        submissions_cursor = db["grading_submissions"].find(f)
        for submission in submissions_cursor:
            # Get assignment info
            assignment = db["assignment"].find_one(
                {"assignment_id": submission["assignment_id"]},
                {"assignment_name": 1, "deadline": 1, "_id": 0}
            )
            submission["assignment_name"] = assignment.get("assignment_name") if assignment else None
            deadline = assignment.get("deadline") if assignment else None

            # Add class and subject names
            class_doc = db["class"].find_one({"class_id": submission["class_id"]}, {"class_name": 1})
            subject_doc = db["subject"].find_one({"subject_id": submission["subject_id"]}, {"subject_name": 1})

            submission["class_name"] = class_doc.get("class_name") if class_doc else None
            submission["subject_name"] = subject_doc.get("subject_name") if subject_doc else None

            # Ensure submit_time_date is datetime
            submit_time = submission.get("submit_time_date")
            if isinstance(submit_time, str):
                submit_time = datetime.fromisoformat(submit_time)

            if isinstance(deadline, str):
                deadline = datetime.fromisoformat(deadline)

            submission["submit_time_date"] = submit_time  # for model parsing

            # Convert to Pydantic model
            try:
                response_model = SubmissionResponse(**submission)
                if deadline and submit_time and submit_time > deadline:
                    late.append(response_model)
                else:
                    on_time.append(response_model)
            except Exception as e:
                print(f"Skipping invalid submission: {e}")
                continue

    return CategorizedSubmissionsResponse(
        on_time_submissions=on_time,
        late_submissions=late
    )



@router.post("/review_auto_graded_marks/{teacher_id}", response_model=SubmissionResponse)
async def review_auto_graded_marks(
    teacher_id: str,
    submission_id: str = Form(...),
    marks: float = Form(...),
    action: str = Form(...)  # "approve" or "modify"
):
    # Validate marks
    if marks < 0 or marks > 100:
        raise HTTPException(status_code=400, detail="Marks must be between 0 and 100.")
    
    # Validate action
    if action not in ["approve", "modify"]:
        raise HTTPException(status_code=400, detail="Action must be 'approve' or 'modify'")

    # Fetch the auto-graded submission
    submission = db["grading_submissions"].find_one({
        "submission_id": submission_id,
        "teacher_id": teacher_id,
        "grading_type": "auto"
    })

    if not submission:
        raise HTTPException(status_code=404, detail="Auto-graded submission not found")

    try:
        # Update marks and change grading_type to "manual"
        update_data = {
            "marks": marks,
            "grading_type": "manual",
            "reviewed_at": datetime.utcnow().isoformat(),
            "review_action": action,
            "original_auto_marks": submission.get("marks")  # Store original AI marks
        }
        
        db["grading_submissions"].update_one(
            {"submission_id": submission_id},
            {"$set": update_data}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update marks: {str(e)}")

    # Return the updated submission
    updated_submission = db["grading_submissions"].find_one({"submission_id": submission_id})
    return SubmissionResponse(**updated_submission)


