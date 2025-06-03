from datetime import datetime
import os
import uuid
from fastapi import APIRouter, File, HTTPException, UploadFile
from typing import List

from ..utils.grading_gemini import grade_answer
from ..utils.grading_deepseek import grade_answer_deepseek
from ..models.academic import AssignmentListResponse, AssignmentViewResponse, ContentResponse, MarksResponse, SubjectResponse,AssignmentMarksResponse, SubmissionResponse
from .database import db
from ..utils.file_utils import extract_text
from ..utils.grading_gemini import grade_answer
from fastapi.responses import FileResponse
from .database import db
from .google_drive import get_drive_service, FOLDER_IDS
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
from ..utils.file_utils import extract_text
from ..utils.grading_gemini import grade_answer
import io
import logging
from tenacity import retry, stop_after_attempt, wait_exponential


logger = logging.getLogger(__name__)
ALLOWED_EXTENSIONS = {"pdf", "txt"}  # Allowed file types

router = APIRouter()


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def upload_to_drive(drive_service, file_metadata, media):
    return drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def download_from_drive(drive_service, file_id):
    request = drive_service.files().get_media(fileId=file_id)
    file_io = io.BytesIO()
    downloader = MediaIoBaseDownload(file_io, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    file_io.seek(0)
    return file_io



@router.get("/content/{content_id}")
async def get_content_by_id(content_id: str):
    try:
        
        content = db["content"].find_one({"content_id": content_id})
        
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")
            
        # Convert ObjectId to string if present
        if "_id" in content:
            content["_id"] = str(content["_id"])
        
        # Format the response to match what the frontend expects
        response = {
            "content_id": content["content_id"],
            "content_name": content.get("content_name", "Untitled"),
            "description": content.get("description", ""),
            "file_path": content.get("content_file_path", "")
        }
            
        return response
    except Exception as e:
        print(f"Error retrieving content metadata: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/content/file/{content_id}")
async def serve_content_file(content_id: str):
    try:
        content = db["content"].find_one({"content_id": content_id})
        
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")

        file_path = content.get("content_file_path")
        print(f"File path: {file_path}")

        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")

        ext = os.path.splitext(file_path)[1].lower()
        media_type = "application/pdf" if ext == ".pdf" else "text/plain" if ext == ".txt" else "application/octet-stream"

        print(f"Serving file: {file_path}, Media type: {media_type}")
        return FileResponse(
            path=file_path,
            media_type=media_type,
            filename=os.path.basename(file_path),
            headers={"Content-Disposition": f"inline; filename={os.path.basename(file_path)}"}
        )
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.get("/assignment/file/{assignment_id}")
async def serve_assignment_file(assignment_id: str):
    try:
        print(f"Looking up assignment_id: {assignment_id}")
        assignment = db["assignment"].find_one({"assignment_id": assignment_id})
        print(f"Content found: {assignment}")

        if not assignment:
            raise HTTPException(status_code=404, detail="Content not found")

        file_path = assignment.get("assignment_file_path")
        print(f"File path: {file_path}")

        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")

        ext = os.path.splitext(file_path)[1].lower()
        media_type = "application/pdf" if ext == ".pdf" else "text/plain" if ext == ".txt" else "application/octet-stream"

        print(f"Serving file: {file_path}, Media type: {media_type}")
        return FileResponse(
            path=file_path,
            media_type=media_type,
            filename=os.path.basename(file_path),
            headers={"Content-Disposition": f"inline; filename={os.path.basename(file_path)}"}
        )
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

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
            assignment_file_id=assignment.get("assignment_file_id"),
            Deadline=assignment.get("deadline"),
            class_id=assignment.get("class_id"),
            subject_id=assignment.get("subject_id"),
            description=assignment.get("description", None) 
        )

        return assignment_response

    except Exception as e:
        print(f"Error processing assignment: {e}")
        raise HTTPException(status_code=500, detail="Error processing assignment data")

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
            upload_date = content.get("upload_date")
            if isinstance(upload_date, str):
                try:
                    upload_date = datetime.fromisoformat(upload_date)
                except ValueError:
                    try:
                        upload_date = datetime.strptime(upload_date, "%Y-%m-%d")
                    except ValueError:
                        upload_date = None
                        
            # Create a ContentResponse object
            content_response = ContentResponse(
                content_id=content.get("content_id"),
                content_name=content.get("content_name"),
                content_file_id=content.get("content_file_id"),
                Date=upload_date,
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


@router.get("/show_assignments/{student_id}/{subject_id}", response_model=AssignmentListResponse)
async def show_assignments(student_id: str, subject_id: str):
    student = db["student"].find_one({"student_id": student_id}, {"_id": 0, "class_id": 1})

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    class_id = student.get("class_id")

    if not class_id:
        raise HTTPException(status_code=404, detail="No class ID associated with this student")

    assignments_cursor = db["assignment"].find(
        {"class_id": class_id, "subject_id": subject_id},
        {"_id": 0, "assignment_id": 1, "assignment_name": 1, "created_at": 1}
    )

    assignments = list(assignments_cursor)

    if not assignments:
        raise HTTPException(status_code=404, detail="No assignments found for this subject and class")

    return AssignmentListResponse(assignments=assignments)


#view assignment (after clicked)
@router.get("/assignment/{assignment_id}", response_model=AssignmentViewResponse)
async def get_assignment(assignment_id: str):
    
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
            assignment_file_id=assignment.get("assignment_file_id"),
            Deadline=assignment.get("deadline"),
            class_id=assignment.get("class_id"),
            subject_id=assignment.get("subject_id"),
            description=assignment.get("description", None) 
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
   
@router.get("/exammarks/{student_id}", response_model=List[MarksResponse])
async def get_exam_marks(student_id: str):
    # Step 1: Fetch all exam_marks documents for the given student_id
    student_exam_docs = db["exam_marks"].find({"student_id": student_id}, {"_id": 0})
    
    marks_responses = []

    found_any = False  # To track if we found any matching documents
    
    for student_exam_data in student_exam_docs:
        found_any = True
        
        class_id = student_exam_data.get("class_id")
        class_doc = db["class"].find_one({"class_id": class_id}, {"class_name": 1, "_id": 0})
        class_name = class_doc.get("class_name") if class_doc else "Class not found"
        exam_year = student_exam_data.get("exam_year")
        exam_marks_list = student_exam_data.get("exam_marks", [])

        for subject_entry in exam_marks_list:
            subject_id = subject_entry.get("subject_id")
            subject_doc = db["subject"].find_one({"subject_id": subject_id}, {"subject_name": 1, "_id": 0})
            subject_name = subject_doc.get("subject_name") if subject_doc else "Subject not found"

            for exam in subject_entry.get("exams", []):
                marks_responses.append(MarksResponse(
                    term=exam.get("term"),
                    subject_id=subject_id,
                    subject_name=subject_name,
                    marks=exam.get("marks"),
                    class_id=class_id,
                    class_name=class_name,
                    exam_year=exam_year
                ))

    if not found_any or not marks_responses:
        raise HTTPException(status_code=404, detail="No exam marks found for this student")

    return marks_responses

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
    assignment_name = assignment.get("assignment_name", "Unnamed Assignment")

    # Fetch class name
    class_doc = db["class"].find_one({"class_id": class_id})
    class_name = class_doc.get("class_name", "Unknown Class") if class_doc else "Unknown Class"

    # Fetch subject name
    subject_doc = db["subject"].find_one({"subject_id": subject_id})
    subject_name = subject_doc.get("subject_name", "Unknown Subject") if subject_doc else "Unknown Subject"

    # Determine collection based on grading type
    collection_name = "grading_submissions" if grading_type == "auto" else "submission"
    
    # Check if a submission already exists for the same student and assignment
    existing_submission = db[collection_name].find_one({"student_id": student_id, "assignment_id": assignment_id})
    submission_id = existing_submission.get("submission_id") if existing_submission else f"SUBM{uuid.uuid4().hex[:6].upper()}"
    
    content = await file.read()
    try:
        drive_service = get_drive_service()
        file_metadata = {
            'name': f"{submission_id}_{file.filename}",
            'parents': [FOLDER_IDS["submissions"]],
            'mimeType': file.content_type
        }
        media = MediaIoBaseUpload(io.BytesIO(content), mimetype=file.content_type)
        file_response = upload_to_drive(drive_service, file_metadata, media)
        google_drive_file_id = file_response.get('id')
    
        # AI Auto-Grading (if grading_type is 'auto')
        marks = None
        if grading_type == "auto" and sample_answer:
            try:
                file_io = download_from_drive(drive_service, google_drive_file_id)
                student_text = extract_text(file_io, file.filename)
                marks = grade_answer(sample_answer, student_text)
            except Exception as e:
                logger.error(f"Auto-grading failed for submission_id={submission_id}: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Auto-grading failed: {str(e)}")
        
        # Submission record
        submission_data = {
            "submission_id": submission_id,
            "subject_id": subject_id,
            "subject_name": subject_name,
            "content_file_id": google_drive_file_id,
            "submit_time_date": datetime.utcnow().isoformat(),
            "class_id": class_id,
            "class_name": class_name,
            "file_name": file.filename,
            "marks": marks,
            "assignment_id": assignment_id,
            "assignment_name": assignment_name,
            "student_id": student_id,
            "teacher_id": teacher_id,
        }

        # Add additional fields for auto-graded submissions
        if grading_type == "auto":
            submission_data.update({
                "grading_type": "auto",
                "auto_graded_at": datetime.utcnow().isoformat(),
                "sample_answer_used": sample_answer
            })

        if existing_submission:
            if existing_submission.get("content_file_id"):
                try:
                    drive_service.files().delete(fileId=existing_submission["content_file_id"]).execute()
                except Exception as e:
                    logger.warning(f"Failed to delete old file {existing_submission['content_file_id']}: {str(e)}")
            # Update the existing submission in appropriate collection
            db[collection_name].update_one(
                {"submission_id": submission_id},
                {"$set": submission_data}
            )
        else:
            # Insert a new submission in appropriate collection
            db[collection_name].insert_one(submission_data)
            
        return SubmissionResponse(**submission_data)
        
    except Exception as e:
        logger.error(f"[ERROR] Submitting submission_id={submission_id} -> {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to submit assignment: {str(e)}")



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

