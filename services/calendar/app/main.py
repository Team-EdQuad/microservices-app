# calendar/main.py 

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
from datetime import datetime, date, timedelta
from pymongo import MongoClient

app = FastAPI(title="Calendar Microservice")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# services/calendar/app/main.py

from fastapi import FastAPI, HTTPException, Query, status
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from pymongo import MongoClient
from pydantic import BaseModel

app = FastAPI()

# --- Database Configuration ---
MONGO_URI = "mongodb+srv://admin:1234@cluster0.ogyx0.mongodb.net/LMS?retryWrites=true&w=majority&appName=Cluster0" # e.g., "mongodb://mongo:27017/" if using Docker Compose
DB_NAME = "LMS"

try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    students_collection = db["student"]
    assignments_collection = db["assignment"]
    print(f"MongoDB connected successfully to database: {DB_NAME}")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    raise

# --- Pydantic Response Model ---
class AssignmentDeadline(BaseModel):
    assignment_id: Optional[str] = None
    assignment_name: str
    deadline: Optional[datetime] = None
    subject_id: str
    teacher_id: Optional[str] = None # Added for teacher's view

# --- Core API Endpoint for Assignment Deadlines ---
@app.get(
    "/assignments/deadlines",
    response_model=List[AssignmentDeadline],
    summary="Fetch assignment deadlines for students or teachers based on various criteria"
)
async def get_assignments_deadlines_internal(
    student_id: Optional[str] = Query(
        None,
        description="The ID of the student for whom to fetch assignment deadlines. "
                    "If provided, deadlines will be filtered by subjects registered by this student. "
                    "Cannot be used with teacher_id simultaneously."
    ),
    teacher_id: Optional[str] = Query(
        None,
        description="The ID of the teacher for whom to fetch assignments they have created. "
                    "Cannot be used with student_id simultaneously."
    ),
    class_id: Optional[str] = Query(None, description="Optional: Filter by a specific class ID."),
    subject_id: Optional[str] = Query(None, description="Optional: Filter by a specific subject ID. "
                                                         "If student_id is also provided, this will filter "
                                                         "within the student's registered subjects."),
    start_date: Optional[date] = Query(
        None, description="Optional: Filter assignments with deadlines on or after this date (YYYY-MM-DD)."
    ),
    end_date: Optional[date] = Query(
        None, description="Optional: Filter assignments with deadlines on or before this date (YYYY-MM-DD)."
    )
) -> List[AssignmentDeadline]:
    """
    Retrieves a list of assignment deadlines.

    **Usage:**
    - Provide `student_id` to get assignments for subjects the student is registered for.
    - Provide `teacher_id` to get assignments created by that teacher.
    - Only one of `student_id` or `teacher_id` can be provided at a time.
    - Other filters (`class_id`, `subject_id`, `start_date`, `end_date`) can be combined.
    """
    query_filters = {}
    registered_subjects = [] # Initialize for student_id path

    # Input validation: Cannot provide both student_id and teacher_id
    if student_id and teacher_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot provide both 'student_id' and 'teacher_id' simultaneously. Please choose one."
        )

    # Handle student_id requirement
    if student_id:
        student = students_collection.find_one({"student_id": student_id})
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student with ID '{student_id}' not found."
            )

        registered_subjects = student.get("subject_id", [])
        if not registered_subjects:
            return [] # Student exists but has no registered subjects

        query_filters["subject_id"] = {"$in": registered_subjects}
        # For student view, we might also want to filter by class_id if the student belongs to a specific class
        # if student.get("class_id"):
        #     query_filters["class_id"] = student["class_id"]

    # Handle teacher_id requirement
    elif teacher_id:
        # Assuming teacher_id directly corresponds to assignments they created
        query_filters["teacher_id"] = teacher_id

    # Apply other filters, considering their interaction with student_id/teacher_id
    if class_id:
        query_filters["class_id"] = class_id

    if subject_id:
        if student_id:
            # If student_id was provided, ensure this subject_id is part of their registered subjects
            if subject_id not in registered_subjects: # registered_subjects from the student query above
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Subject '{subject_id}' is not registered by student '{student_id}'. "
                            "Cannot filter deadlines for this subject."
                )
            # If it is in registered_subjects, narrow the $in query to just this subject
            query_filters["subject_id"] = subject_id
        else:
            # If no student_id, just filter by the provided subject_id
            query_filters["subject_id"] = subject_id

    # Apply date range filters
    if start_date or end_date:
        deadline_query = {}
        if start_date:
            deadline_query["$gte"] = datetime.combine(start_date, datetime.min.time())
        if end_date:
            deadline_query["$lte"] = datetime.combine(end_date, datetime.max.time())
        query_filters["deadline"] = deadline_query

    # Fetch assignments from the 'assignment' collection
    projection = {
        "assignment_id": 1,
        "assignment_name": 1,
        "deadline": 1,
        "subject_id": 1,
        "teacher_id": 1, # Include teacher_id in projection
        "class_id": 1, # Include class_id in projection for more flexible display
        "_id": 0 # Exclude default _id
    }

    try:
        assignments_cursor = assignments_collection.find(query_filters, projection)

        deadlines_list = []
        for assignment in assignments_cursor:
            deadline_val = assignment.get("deadline")
            if isinstance(deadline_val, dict) and "$date" in deadline_val:
                try:
                    deadline_val = datetime.fromisoformat(deadline_val["$date"].replace('Z', '+00:00'))
                except ValueError:
                    deadline_val = None
            
            deadlines_list.append(AssignmentDeadline(
                assignment_id=assignment.get("assignment_id"),
                assignment_name=assignment.get("assignment_name"),
                deadline=deadline_val,
                subject_id=assignment.get("subject_id"),
                teacher_id=assignment.get("teacher_id"), # Assign fetched teacher_id
                class_id=assignment.get("class_id") # Assign fetched class_id
            ))
        
        return deadlines_list

    except Exception as e:
        print(f"An error occurred while fetching assignments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

# Optional: Health check endpoint for the calendar microservice itself
@app.get("/health", summary="Health check for Calendar Service")
async def health_check():
    try:
        client.admin.command('ping')
        return {"status": "ok", "message": "Calendar service is healthy and connected to MongoDB."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to connect to MongoDB: {e}"
        )