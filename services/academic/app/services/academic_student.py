from datetime import datetime
import os
import uuid
from fastapi import APIRouter, File, HTTPException, UploadFile
from typing import List
from ..models.academic import AssignmentListResponse, AssignmentViewResponse, ContentResponse, MarksResponse, SubjectResponse,AssignmentMarksResponse, SubmissionResponse
from .database import db
from ..utils.file_utils import extract_text
from ..utils.grading import grade_answer



UPLOAD_DIR = "uploads/submissions"
os.makedirs(UPLOAD_DIR, exist_ok=True) 

ALLOWED_EXTENSIONS = {"pdf", "txt"}  # Allowed file types


router = APIRouter()

#subject interface
@router.get("/students/{student_id}/subjects", response_model=List[SubjectResponse])
async def get_subject_names(student_id: str):
    # Fetch student document from 'students' collection
    student = db["student"].find_one({"student_id": student_id})
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    subject_ids = student.get("subject_id", [])
    
    if not subject_ids:
        raise HTTPException(status_code=404, detail="No subject IDs associated with this student")
    
    # Fixed field name to match actual database (lowercase)
    subjects_cursor = db["subject"].find(
        {"subject_id": {"$in": subject_ids}},
        {"_id": 0, "subject_id": 1, "subject_name": 1}  # Fixed field names
    )
    
    subjects_list = list(subjects_cursor)
    
    if not subjects_list:
        raise HTTPException(status_code=404, detail="Subjects not found")
    
    # Map database fields to Pydantic model fields
    subjects = []
    for subject in subjects_list:
        # Convert from database field names to Pydantic model field names
        subjects.append(SubjectResponse(
            Subject_id=subject["subject_id"],
            SubjectName=subject["subject_name"]
        ))
    
    return subjects

#view content 
@router.get("/content/{student_id}/{subject_id}", response_model=List[ContentResponse])
async def get_content(student_id: str, subject_id: str):
    # Step 1: Fetch student document
    student = db["student"].find_one({"student_id": student_id}, {"_id": 0, "class_id": 1})
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    class_id = student.get("class_id")
    
    if not class_id:
        raise HTTPException(status_code=404, detail="No class ID associated with this student")
    
    # Step 2: Fetch content details where class_id matches
    content_cursor = db["content"].find(
        {"subject_id": subject_id,"class_id": class_id},
        {"_id": 0}
    )
    
    content_list = []
    for content in content_cursor:
        try:
            # Handle Date field
            if "Date" in content:
                if isinstance(content["Date"], str):
                    try:
                        content["Date"] = datetime.fromisoformat(content["Date"])
                    except ValueError:
                        try:
                            content["Date"] = datetime.strptime(content["Date"], "%Y-%m-%d")
                        except ValueError:
                            content["Date"] = None
            
            # Create a ContentResponse object
            content_response = ContentResponse(
                content_id=content.get("content_id"),
                content_name=content.get("content_name"),
                content_file_path=content.get("content_file_path"),
                Date=content.get("Date"),
                description=content.get("description"),
                class_id=content.get("class_id"),
                subject_id=content.get("subject_id", "")  
            )
            
            content_list.append(content_response)
        except Exception as e:
            print(f"Error processing content item: {e}")
            # Continue to the next item
    
    if not content_list:
        raise HTTPException(status_code=404, detail="No content found for this class")
    
    return content_list



#view all available assignments
@router.get("/show_assignments/{student_id}/{subject_id}", response_model=AssignmentListResponse)
async def show_assignments(student_id: str, subject_id: str):
    # Step 1: Get student's class_id
    student = db["student"].find_one({"student_id": student_id}, {"_id": 0, "class_id": 1})

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    class_id = student.get("class_id")

    if not class_id:
        raise HTTPException(status_code=404, detail="No class ID associated with this student")

    # Step 2: Fetch all assignments that match class_id and subject_id
    assignments_cursor = db["assignment"].find(
        {"class_id": class_id, "subject_id": subject_id},
        {"_id": 0, "assignment_id": 1, "assignment_name": 1}
    )

    assignments = list(assignments_cursor)

    if not assignments:
        raise HTTPException(status_code=404, detail="No assignments found for this subject and class")

    # Step 3: Format and return the list
    return AssignmentListResponse(assignments=assignments)


#view assignment (after clicked)
@router.get("/assignment/{assignment_id}", response_model=AssignmentViewResponse)
async def get_assignment(assignment_id: str):
    # Step 1: Fetch assignment by assignment_id only
    assignment = db["assignment"].find_one(
        {"assignment_id": assignment_id},
        {"_id": 0}  # Exclude MongoDB internal ID
    )

    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    try:
        # Step 2: Handle Deadline format
        if "deadline" in assignment:
            if isinstance(assignment["deadline"], str):
                try:
                    assignment["deadline"] = datetime.fromisoformat(assignment["deadline"])
                except ValueError:
                    try:
                        assignment["deadline"] = datetime.strptime(assignment["deadline"], "%Y-%m-%d")
                    except ValueError:
                        assignment["deadline"] = None

        # Step 3: Construct and return response
        assignment_response = AssignmentViewResponse(
            assignment_id=assignment.get("assignment_id"),
            assignment_name=assignment.get("assignment_name"),
            assignment_file_path=assignment.get("assignment_file_path"),
            Deadline=assignment.get("deadline"),
            class_id=assignment.get("class_id"),
            subject_id=assignment.get("subject_id")
        )

        return assignment_response

    except Exception as e:
        print(f"Error processing assignment: {e}")
        raise HTTPException(status_code=500, detail="Error processing assignment data")


#view assignment marks
@router.get("/submissionmarks/{student_id}", response_model=List[AssignmentMarksResponse])
async def get_submission_marks(student_id: str):
    # Step 1: Fetch all submissions for this student
    submissions_cursor = db["submission"].find({"student_id": student_id}, {"_id": 0})
    
    # Convert cursor to list
    submission_list = list(submissions_cursor)
    
    if not submission_list:
        raise HTTPException(status_code=404, detail="No submissions found for this student")
    
    print(f"Found {len(submission_list)} submissions for student {student_id}")
    
    # Map database fields to Pydantic model fields
    submissions_responses = []
    for submission in submission_list:
        assignment_id = submission.get("assignment_id")
        assignment_name = None
        if assignment_id:
            assignment_doc = db["assignment"].find_one({"assignment_id": assignment_id}, {"_id": 0, "assignment_name": 1})
            if assignment_doc:
                assignment_name = assignment_doc.get("assignment_name")
        
        # Get subject name from subject collection
        subject_id = submission.get("subject_id")
        subject_name = None
        if subject_id:
            subject_doc = db["subject"].find_one({"subject_id": subject_id}, {"_id": 0, "subject_name": 1})
            if subject_doc:
                subject_name = subject_doc.get("subject_name")

        submissions_responses.append(AssignmentMarksResponse(
            teacher_id=submission.get("teacher_id"),
            subject_id=submission.get("subject_id"),
            assignment_id=submission.get("assignment_id"),
            assignment_name=assignment_name,
            subject_name=subject_name,
            marks=submission.get("marks", 0)  # Default to 0 if marks not found
        ))
    
    return submissions_responses
   

#view exam marks
@router.get("/exammarks/{student_id}", response_model=List[MarksResponse])
async def get_exam_marks(student_id: str):
    # Step 1: Fetch the exam_marks document for the given student_id
    student_exam_data = db["exam_marks"].find_one({"student_id": student_id}, {"_id": 0})
    
    if not student_exam_data:
        raise HTTPException(status_code=404, detail="No exam marks found for this student")
    
    # Step 2: Fetch class_name from the class collection using class_id
    class_id = student_exam_data.get("class_id")
    class_doc = db["class"].find_one({"class_id": class_id}, {"class_name": 1, "_id": 0})
    class_name = class_doc.get("class_name") if class_doc else "Class not found"
    
    # Step 3: Extract and process exam marks from the nested structure
    marks_responses = []
    exam_marks_list = student_exam_data.get("exam_marks", [])
    
    for subject_entry in exam_marks_list:  # Loop over each subject's marks
        subject_id = subject_entry.get("subject_id")
        
        # Fetch subject_name from the subject collection using subject_id
        subject_doc = db["subject"].find_one({"subject_id": subject_id}, {"subject_name": 1, "_id": 0})
        subject_name = subject_doc.get("subject_name") if subject_doc else "Subject not found"
        
        for exam in subject_entry.get("exams", []):  # Loop over the exams within each subject
            marks_responses.append(MarksResponse(
                term=exam.get("term"),
                subject_id=subject_id,
                subject_name=subject_name,
                marks=exam.get("marks"),
                class_id=class_id,
                class_name=class_name
            ))
    
    if not marks_responses:
        raise HTTPException(status_code=404, detail="No exam marks found")
    
    return marks_responses


#Submission 
@router.post("/submission/{student_id}/{assignment_id}", response_model=SubmissionResponse)
async def submit_assignment(student_id: str, assignment_id: str, file: UploadFile = File(...)):
    # Validate file extension
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only PDF and TXT files are allowed.")

    # Fetch assignment details from MongoDB
    assignment = db["assignment"].find_one({"assignment_id": assignment_id})
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    subject_id = assignment.get("subject_id")
    teacher_id = assignment.get("teacher_id")
    class_id = assignment.get("class_id")
    grading_type = assignment.get("grading_type")
    sample_answer = assignment.get("sample_answer")

    # Check if a submission already exists for the same student and assignment
    existing_submission = db["submission"].find_one({"student_id": student_id, "assignment_id": assignment_id})
    if existing_submission:
        # If a submission exists, delete the old file
        old_file_path = existing_submission.get("content_file_path")
        if old_file_path and os.path.exists(old_file_path):
            os.remove(old_file_path)

    # Generate unique submission ID (reuse existing one if available)
    submission_id = existing_submission.get("submission_id") if existing_submission else f"SUBM{uuid.uuid4().hex[:6].upper()}"

    # Create file path
    file_name = f"{submission_id}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, file_name)

    try:
        # Save uploaded file
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # AI Auto-Grading (if grading_type is 'auto')
    marks = None
    if grading_type == "auto" and sample_answer:
        try:
            student_text = extract_text(file_path)
            marks = grade_answer(sample_answer, student_text)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Auto-grading failed: {str(e)}")

    # Submission record
    submission_data = {
        "submission_id": submission_id,
        "subject_id": subject_id,
        "content_file_path": file_path,
        "submit_time_date": datetime.utcnow().isoformat(),
        "status": True,
        "class_id": class_id,
        "file_name": file.filename,
        "marks": marks,  # Marks assigned if auto-grading is enabled
        "assignment_id": assignment_id,
        "student_id": student_id,
        "teacher_id": teacher_id,
    }

    try:
        if existing_submission:
            # Update the existing submission
            db["submission"].update_one(
                {"submission_id": submission_id},
                {"$set": submission_data}
            )
        else:
            # Insert a new submission
            db["submission"].insert_one(submission_data)
    except Exception as e:
        # Cleanup file if DB operation fails
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Failed to save submission: {str(e)}")

    return SubmissionResponse(**submission_data)



#update content status  (mark as done)
@router.post("/content/{content_id}")
async def update_content_status(content_id: str):
    # Step 1: Fetch class_id and subject_id from the content collection
    content = db["content"].find_one({"content_id": content_id})
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    class_id = content.get("class_id")
    subject_id = content.get("subject_id")
    
    # Step 2: Fetch teacher_id from the teacher collection using class_id
    teacher = db["teacher"].find_one({"class_id": class_id})
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found for this class")
    
    teacher_id = teacher.get("teacher_id")
    
    # Step 3: Update or Insert (Upsert) in student_content_status
    result = db["student_content_status"].update_one(
        {"class_id": class_id, "subject_id": subject_id, "content_id": content_id},
        {
            "$set": {
                "class_id": class_id,
                "subject_id": subject_id,
                "content_status": True
            },
            "$inc": {
                "access_frequency": 1  # Increment access frequency by 1 on every content click
            }
        },
        upsert=True  # Insert a new document if no match is found
    )
    
    # Step 4: Return success message
    if result.modified_count or result.upserted_id:
        return {"message": "Content status updated successfully", "class_id": class_id, "subject_id": subject_id, "teacher_id": teacher_id}
    else:
        return {"message": "Content status update failed"}

