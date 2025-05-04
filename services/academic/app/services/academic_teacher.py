from datetime import datetime
import os
import uuid
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from typing import List
from ..models.academic import AssignmentResponse, ClassResponse, ContentUploadResponse,SubjectClassResponse, SubjectResponse,SubmissionResponse
from .database import db



ASSIGNMENT_DIR = "uploads/assignments"
os.makedirs(ASSIGNMENT_DIR, exist_ok=True) 

UPLOAD_DIR = "uploads/content/"  # Directory to save uploaded files
os.makedirs(UPLOAD_DIR, exist_ok=True)
ALLOWED_EXTENSIONS = {"pdf", "txt", "mp3", "mp4"}  # Allowed file types


router = APIRouter()
#view accessible subject and class  ( teacher )
@router.get("/subjectNclass/{teacher_id}", response_model=SubjectClassResponse)
async def get_subjectNclass(teacher_id: str):
    # Fetch teacher document
    teacher = db["teacher"].find_one({"teacher_id": teacher_id})
    
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    subject_ids = teacher.get("subject_id", [])
    class_ids = teacher.get("class_id", [])
    
    if not subject_ids:
        raise HTTPException(status_code=404, detail="No subject IDs associated with this teacher")
    if not class_ids:
        raise HTTPException(status_code=404, detail="No class IDs associated with this teacher")
    
    # Ensure subject_ids and class_ids are lists
    if not isinstance(subject_ids, list):
        subject_ids = [subject_ids]
    if not isinstance(class_ids, list):
        class_ids = [class_ids]
    
    # Get subjects and classes
    subjects_cursor = db["subject"].find(
        {"subject_id": {"$in": subject_ids}},
        {"_id": 0, "subject_id": 1, "subject_name": 1}
    )
    
    class_cursor = db["class"].find(
        {"class_id": {"$in": class_ids}},
        {"_id": 0, "class_id": 1, "class_name": 1}
    )
    
    subjects_list = list(subjects_cursor)
    class_list = list(class_cursor)
    
    if not subjects_list:
        raise HTTPException(status_code=404, detail="Subjects not found")
    if not class_list:
        raise HTTPException(status_code=404, detail="Classes not found")
    
    # Create response objects
    subjects = []
    classes = []
    
    for subject in subjects_list:
        subjects.append(SubjectResponse(
            Subject_id=subject["subject_id"],
            SubjectName=subject["subject_name"]
        ))
    
    for cls in class_list:
        classes.append(ClassResponse(
            class_id=cls["class_id"],
            class_name=cls["class_name"]
        ))
    
    # Return combined response
    return SubjectClassResponse(subjects=subjects, classes=classes)


@router.post("/assignmentcreate/{class_id}/{subject_id}/{teacher_id}", response_model=AssignmentResponse)
async def create_assignment(
    class_id: str,
    subject_id: str,
    teacher_id: str,
    assignment_name: str = Form(...),
    description: str = Form(...),
    deadline: str = Form(...),  # ISO format string
    grading_type: str = Form(...),
    sample_answer: str = Form(None),
    file: UploadFile = File(...)
):
    # ✅ Validate grading type
    if grading_type == "auto" and not sample_answer:
        raise HTTPException(status_code=400, detail="Sample answer is required for auto grading.")

    # ✅ Generate ID and file path
    assignment_id = f"ASM{uuid.uuid4().hex[:6].upper()}"
    file_name = f"{assignment_id}_{file.filename}"

    # ✅ Ensure directory exists
    os.makedirs(ASSIGNMENT_DIR, exist_ok=True)
    file_path = os.path.join(ASSIGNMENT_DIR, file_name)

    # ✅ Save uploaded file
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # ✅ Convert deadline safely
    try:
        deadline_dt = datetime.fromisoformat(deadline)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid deadline format. Use ISO format (e.g., 2025-04-30T23:59:00)")

    # ✅ Get current UTC time for upload timestamp
    created_at = datetime.utcnow()

    # ✅ Insert data
    assignment_data = {
        "assignment_id": assignment_id,
        "assignment_name": assignment_name,
        "description": description,
        "deadline": deadline_dt,
        "assignment_file_path": file_path,
        "class_id": class_id,
        "subject_id": subject_id,
        "teacher_id": teacher_id,
        "grading_type": grading_type,
        "sample_answer": sample_answer if grading_type == "auto" else None,
        "created_at": datetime.utcnow()
    }

    db["assignment"].insert_one(assignment_data)
    return AssignmentResponse(**assignment_data)






#upload content
@router.post("/contentupload/{class_id}/{subject_id}", response_model=ContentUploadResponse)
async def upload_content(
    class_id: str,
    subject_id: str,
    file: UploadFile = File(...),
    content_name: str = Form(...),
    description: str = Form(...),
):
    # Validate file extension
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only PDF, TXT, MP3, and MP4 files are allowed.")

    # Generate unique content ID
    content_id = f"CNT{uuid.uuid4().hex[:3].upper()}"

    # Create file path
    file_name = f"{content_id}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, file_name)

    try:
        # Save uploaded file
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Content record
    content_data = {
        "content_id": content_id,
        "content_name": content_name,
        "content_file_path": file_path,
        "upload_date": datetime.utcnow().strftime("%Y-%m-%d"),  # Only store date
        "description": description,
        "class_id": class_id,
        "subject_id": subject_id,
    }

    try:
        # Insert content into MongoDB
        db["content"].insert_one(content_data)
    except Exception as e:
        # Cleanup file if DB insert fails
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Failed to save content: {str(e)}")

    return ContentUploadResponse(**content_data)


##view submissions 
@router.get("/submission_view/{teacher_id}", response_model=List[SubmissionResponse])
async def view_manual_submission(teacher_id: str):
    teacher_data = db["teacher"].find_one({"teacher_id": teacher_id})
    if not teacher_data:
        raise HTTPException(status_code=404, detail="Teacher not found")

    accessible_classes = teacher_data.get("class_id", [])
    accessible_subjects = teacher_data.get("subject_id", [])

    # Find ungraded submissions from classes and subjects the teacher has access to
    submissions_cursor = db["submission"].find({
        "teacher_id": teacher_id,
        "class_id": {"$in": accessible_classes},
        "subject_id": {"$in": accessible_subjects},
        "marks": None  # marks null means it's ungraded (manual)
    })

    manual_submissions = []
    for submission in submissions_cursor:
        # Fetch related assignment info (optional)
        assignment = db["assignment"].find_one({"assignment_id": submission["assignment_id"]})
        if assignment:
            submission["assignment_name"] = assignment.get("assignment_name")
        manual_submissions.append(submission)

    if not manual_submissions:
        raise HTTPException(status_code=404, detail="No manual submissions found")

    return [SubmissionResponse(**submission) for submission in manual_submissions]


#manual submissions marks add ( teacher )
@router.post("/update_submission_marks/{teacher_id}", response_model=SubmissionResponse)
async def update_submission_marks(
    teacher_id: str,
    submission_id: str = Form(...),
    marks: float = Form(...),
):
    # Validate marks
    if marks < 0 or marks > 100:
        raise HTTPException(status_code=400, detail="Marks must be between 0 and 100.")

    # Fetch submission details from MongoDB
    submission = db["submission"].find_one({"submission_id": submission_id})
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    # Verify that the teacher has permission to grade this submission
    if submission["teacher_id"] != teacher_id:
        raise HTTPException(status_code=403, detail="You do not have permission to grade this submission")

    # Check if the submission is manual grading type
    assignment = db["assignment"].find_one({"assignment_id": submission["assignment_id"]})
    if not assignment or assignment.get("grading_type") != "manual":
        raise HTTPException(status_code=400, detail="Only manual grading submissions can be updated")

    # Update the marks in the submission record
    try:
        db["submission"].update_one(
            {"submission_id": submission_id},
            {"$set": {"marks": marks}}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update marks: {str(e)}")

    # Fetch updated submission for response
    updated_submission = db["submission"].find_one({"submission_id": submission_id})
    return SubmissionResponse(**updated_submission)


#enter exam marks of student ( teacher )
@router.post("/update_exam_marks", response_model=dict)
async def add_exam_marks(
    teacher_id: str = Form(...),
    student_id: str = Form(...),
    exam_year: int = Form(...),
    subject_name: str = Form(...),  # Teacher enters subject name
    term: int = Form(...),
    marks: float = Form(...),
):
    # Fetch class_id from student collection based on student_id
    student = db["student"].find_one({"student_id": student_id})
    if not student:
        raise HTTPException(status_code=404, detail=f"Student with ID {student_id} not found.")
    
    class_id = student["class_id"]  # Automatically retrieve class_id from student record

    # Fetch subject_id from subject collection based on subject_name
    subject = db["subject"].find_one({"subject_name": subject_name})
    if not subject:
        raise HTTPException(status_code=404, detail=f"Subject with name '{subject_name}' not found.")
    
    subject_id = subject["subject_id"]  # Automatically retrieve subject_id

    # Generate a unique exam_id for the new exam entry
    exam_id = f"EXM{uuid.uuid4().hex[:6].upper()}"

    # Check if the student already has exam marks for the given year
    existing_record = db["exam_marks"].find_one({"student_id": student_id, "exam_year": exam_year})

    if existing_record:
        # Check if the subject_id already exists in the student's record
        subject_found = False
        for subject_exam in existing_record["exam_marks"]:
            if subject_exam["subject_id"] == subject_id:
                subject_found = True
                # Append the new exam data to the existing subject's exams list
                subject_exam["exams"].append({
                    "exam_id": exam_id,
                    "term": term,
                    "marks": marks,
                })
                break

        # If subject_id doesn't exist, add it as a new subject
        if not subject_found:
            existing_record["exam_marks"].append({
                "subject_id": subject_id,
                "subject_name": subject_name,
                "exams": [
                    {
                        "exam_id": exam_id,
                        "term": term,
                        "marks": marks,
                    }
                ],
            })

        # Update the existing record in the database
        db["exam_marks"].update_one(
            {"student_id": student_id, "exam_year": exam_year},
            {"$set": {"exam_marks": existing_record["exam_marks"]}},
        )
        message = f"Updated marks for student {student_id}."
    else:
        # Create a new record if it doesn't already exist
        exam_marks_data = {
            "student_id": student_id,
            "exam_year": exam_year,
            "class_id": class_id,
            "teacher_id": teacher_id,
            "exam_marks": [
                {
                    "subject_id": subject_id,
                    "subject_name": subject_name,
                    "exams": [
                        {
                            "exam_id": exam_id,
                            "term": term,
                            "marks": marks,
                        }
                    ],
                }
            ],
        }
        # Insert new record into the database
        db["exam_marks"].insert_one(exam_marks_data)
        message = f"Created new record and added marks for student {student_id}."

    return {"detail": message}








# #asssignment create ( teacher )
# @router.post("/assignmentcreate/{class_id}/{subject_id}/{teacher_id}", response_model=AssignmentResponse)
# async def create_assignment(
#     class_id: str,
#     subject_id: str,
#     teacher_id: str,
#     assignment_name: str = Form(...),
#     description: str = Form(...),
#     deadline: str = Form(...),  # ISO format string
#     grading_type: str = Form(...),  # "manual" or "auto"
#     sample_answer: str = Form(None),  # Required if grading_type is "auto"
#     file: UploadFile = File(...)
# ):
#     # Validate grading type
#     if grading_type == "auto" and not sample_answer:
#         raise HTTPException(status_code=400, detail="Sample answer is required for auto grading.")

#     # Generate unique assignment ID
#     assignment_id = f"ASM{uuid.uuid4().hex[:6].upper()}"

#     # Create file path
#     file_name = f"{assignment_id}_{file.filename}"
#     file_path = os.path.join(ASSIGNMENT_DIR, file_name)

#     # Save file
#     with open(file_path, "wb") as f:
#         f.write(await file.read())

#     # Create assignment record
#     assignment_data = {
#         "assignment_id": assignment_id,
#         "assignment_name": assignment_name,
#         "description": description,
#         "deadline": datetime.fromisoformat(deadline),
#         "assignment_file_path": file_path,
#         "class_id": class_id,
#         "subject_id": subject_id,
#         "teacher_id": teacher_id,
#         "grading_type": grading_type,
#         "sample_answer": sample_answer if grading_type == "auto" else None
#     }

#     # Insert into MongoDB
#     db["assignment"].insert_one(assignment_data)

#     return AssignmentResponse(**assignment_data)





