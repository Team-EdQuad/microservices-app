from datetime import datetime
import os
import uuid
from fastapi import APIRouter, File, HTTPException, UploadFile
from typing import List
from ..utils.grading_gemini import grade_answer
from ..models.academic import StatusUpdateRequest,AssignmentListResponse, AssignmentViewResponse, ContentResponse, MarksResponse, SubjectResponse,AssignmentMarksResponse, SubmissionResponse
from .database import db
from ..utils.file_utils import extract_text
from ..utils.grading_gemini import grade_answer
from fastapi.responses import FileResponse
from .database import db
from ..utils.file_utils import extract_text
from ..utils.grading_gemini import grade_answer
import io
import logging
import aiofiles
import mimetypes
from fastapi.staticfiles import StaticFiles
from pathlib import Path


logger = logging.getLogger(__name__)
UPLOAD_DIR = "local_uploads"
ALLOWED_EXTENSIONS = {"pdf", "txt"}  # Allowed file types

router = APIRouter()

@router.get("/content/file/{content_id}")
async def serve_content_file(content_id: str):
    try:
        # 1. Find the content document in the database
        content = db["content"].find_one({"content_id": content_id})
        if not content:
            raise HTTPException(status_code=404, detail="Content metadata not found in the database.")

        # 2. Get the file path directly from the database record
        file_path = content.get("content_file_path")

        # 3. Critically validate the path and file existence
        if not file_path:
            raise HTTPException(status_code=404, detail="The database record is missing a file path.")

        # This is the most important check. It uses the exact path from the DB.
        if not os.path.exists(file_path):
            # We log this for clear debugging. Check your server console for this message.
            print(f"[ERROR] CRITICAL: File does not exist at the path from the database: {file_path}")
            raise HTTPException(status_code=404, detail=f"File not found on the server's disk.")


        ext = os.path.splitext(file_path)[1].lower()
        media_type = "application/pdf" if ext == ".pdf" else "text/plain" if ext == ".txt" else "application/octet-stream"

        return FileResponse(
            path=file_path,
            media_type=media_type,
            filename=os.path.basename(file_path),
            headers={"Content-Disposition": f"inline; filename={os.path.basename(file_path)}"}
        )
    except Exception as e:
        # Catch any other unexpected crash and log it
        print(f"[CRITICAL ERROR] An unexpected exception occurred in serve_content_file: {e}")
        raise HTTPException(status_code=500, detail="A critical internal error occurred while processing the file.")
    
    
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
            assignment_file_path=assignment.get("assignment_file_path"),
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
                content_file_path=content.get("content_file_path"),
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


# View assignment marks from both submission and grading_submission
@router.get("/submissionmarks/{student_id}", response_model=List[AssignmentMarksResponse])
async def get_submission_marks(student_id: str):
    # Step 1: Fetch submissions from both collections
    submission_cursor = db["submission"].find({"student_id": student_id}, {"_id": 0})
    grading_cursor = db["grading_submissions"].find({"student_id": student_id}, {"_id": 0})
    
    submission_list = list(submission_cursor)
    grading_list = list(grading_cursor)
    
    # Combine both lists
    combined_submissions = submission_list + grading_list

    if not combined_submissions:
        raise HTTPException(status_code=404, detail="No submissions found for this student")
    
    print(f"Found {len(combined_submissions)} total submissions for student {student_id}")
    
    # Prepare response
    submissions_responses = []
    for submission in combined_submissions:
        assignment_id = submission.get("assignment_id")
        assignment_name = submission.get("assignment_name")
        if not assignment_name and assignment_id:
            # Fallback: get from assignment collection
            assignment_doc = db["assignment"].find_one({"assignment_id": assignment_id}, {"_id": 0, "assignment_name": 1})
            if assignment_doc:
                assignment_name = assignment_doc.get("assignment_name")

        subject_id = submission.get("subject_id")
        subject_name = submission.get("subject_name")
        if not subject_name and subject_id:
            # Fallback: get from subject collection
            subject_doc = db["subject"].find_one({"subject_id": subject_id}, {"_id": 0, "subject_name": 1})
            if subject_doc:
                subject_name = subject_doc.get("subject_name")

        submissions_responses.append(AssignmentMarksResponse(
            teacher_id=submission.get("teacher_id"),
            subject_id=subject_id,
            assignment_id=assignment_id,
            assignment_name=assignment_name,
            subject_name=subject_name,
            marks=submission.get("marks", 0)
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

    # Fetch assignment details
    assignment = db["assignment"].find_one({"assignment_id": assignment_id})
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    # Get necessary details from assignment
    subject_id = assignment.get("subject_id")
    teacher_id = assignment.get("teacher_id")
    class_id = assignment.get("class_id")
    grading_type = assignment.get("grading_type")
    sample_answer = assignment.get("sample_answer")
    assignment_name = assignment.get("assignment_name", "Unnamed Assignment")

    # Fetch related names for the record
    class_doc = db["class"].find_one({"class_id": class_id})
    class_name = class_doc.get("class_name", "Unknown Class") if class_doc else "Unknown Class"
    subject_doc = db["subject"].find_one({"subject_id": subject_id})
    subject_name = subject_doc.get("subject_name", "Unknown Subject") if subject_doc else "Unknown Subject"

    # Determine collection and check for existing submission
    collection_name = "grading_submissions" if grading_type == "auto" else "submission"
    existing_submission = db[collection_name].find_one({"student_id": student_id, "assignment_id": assignment_id})
    
    submission_id = existing_submission.get("submission_id") if existing_submission else f"SUBM{uuid.uuid4().hex[:6].upper()}"

    # Define local file path and save the file
    submissions_path = os.path.join(UPLOAD_DIR, "submissions")
    os.makedirs(submissions_path, exist_ok=True)
    
    file_path = os.path.join(submissions_path, f"{submission_id}_{file.filename}")

    try:
        content = await file.read()
        async with aiofiles.open(file_path, 'wb') as out_file:
            await out_file.write(content)
        
        # AI Auto-Grading (if applicable)
        marks = None
        if grading_type == "auto" and sample_answer:
            try:
                # Use the in-memory content for text extraction, which is more efficient
                student_text = extract_text(io.BytesIO(content), file.filename)
                marks = grade_answer(sample_answer, student_text)
            except Exception as e:
                logger.error(f"Auto-grading failed for submission_id={submission_id}: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Auto-grading failed: {str(e)}")
        
        # Prepare the submission record with the local file path
        submission_data = {
            "submission_id": submission_id,
            "subject_id": subject_id,
            "subject_name": subject_name,
            "content_file_path": file_path,  # Store the local path
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

        if grading_type == "auto":
            submission_data.update({
                "grading_type": "auto",
                "auto_graded_at": datetime.utcnow().isoformat(),
                "sample_answer_used": sample_answer
            })

        # Handle resubmission: delete old file and update record
        if existing_submission:
            old_file_path = existing_submission.get("content_file_path")
            if old_file_path and os.path.exists(old_file_path):
                try:
                    os.remove(old_file_path)
                except OSError as e:
                    logger.warning(f"Failed to delete old file {old_file_path}: {e}")
            
            db[collection_name].update_one(
                {"submission_id": submission_id},
                {"$set": submission_data}
            )
        else:
            # Insert a new record
            db[collection_name].insert_one(submission_data)
            
        return SubmissionResponse(**submission_data)
        
    except Exception as e:
        logger.error(f"[ERROR] Submitting submission_id={submission_id} -> {str(e)}")
        # Clean up the newly created file if something went wrong
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Failed to submit assignment: {str(e)}")


# update content status (mark as done)
@router.post("/content/{content_id}")
async def update_content_status(content_id: str, payload: StatusUpdateRequest):
    student_id = payload.student_id

    # Step 1: Fetch details from the content collection
    content = db["content"].find_one({"content_id": content_id})
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    class_id = content.get("class_id")
    subject_id = content.get("subject_id")
    
    # Step 2: Update or Insert the student's content status
    result = db["student_content"].update_one(
        # Filter remains the same
        {
            "student_id": student_id, 
            "content_id": content_id,
            "subject_id": subject_id
        },
        {
            "$set": {
                "student_id": student_id,
                "content_id": content_id,
                "class_id": class_id,
                "subject_id": subject_id,
                # --- THIS IS THE CORRECTED LINE ---
                # Now matches your data structure: status: "Active"
                "status": "Active"  
            },
        },
        upsert=True
    )
    
    # Step 3: Return success message using the robust check
    if result.modified_count or result.upserted_id or result.matched_count > 0:
        return {
            "message": "Content status is successfully marked as complete", 
            "student_id": student_id,
            "class_id": class_id, 
            "subject_id": subject_id, 
        }
    else:
        return {"message": "Content status update failed for an unknown reason"}
