# services/calendar/main.py 

# from fastapi import FastAPI, HTTPException, Query
# from fastapi.middleware.cors import CORSMiddleware
# from typing import List, Dict, Any
# from datetime import datetime, date, timedelta

# app = FastAPI(title="Calendar Microservice")

# # CORS settings for the Calendar microservice
# # Allow your frontend (http://localhost:5173) and API Gateway (http://127.0.0.1:8000)
# # to access this service.
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:5173", "http://127.0.0.1:8000"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # --- Database Simulation (Replace with actual DB logic) ---
# # In a real application, you would connect to a database (e.g., MongoDB, PostgreSQL)
# # and fetch actual assignment data. This is a placeholder.
# sample_assignments_db = [
#     {"assignment_id": "ASS001", "name": "Math Homework 1", "deadline": "2025-07-10", "class_id": "CLS001", "subject_id": "SUB001"},
#     {"assignment_id": "ASS002", "name": "Science Project", "deadline": "2025-07-15", "class_id": "CLS001", "subject_id": "SUB002"},
#     {"assignment_id": "ASS003", "name": "History Essay", "deadline": "2025-07-12", "class_id": "CLS002", "subject_id": "SUB003"},
#     {"assignment_id": "ASS004", "name": "Physics Lab Report", "deadline": "2025-07-20", "class_id": "CLS001", "subject_id": "SUB004"},
#     {"assignment_id": "ASS005", "name": "Chemistry Quiz", "deadline": "2025-07-08", "class_id": "CLS002", "subject_id": "SUB005"},
#     {"assignment_id": "ASS006", "name": "Art Sketch", "deadline": "2025-07-11", "class_id": "CLS001", "subject_id": "SUB006"},
#     {"assignment_id": "ASS007", "name": "Literature Reading", "deadline": "2025-07-18", "class_id": "CLS001", "subject_id": "SUB001"},
# ]

# @app.get("/assignments/deadlines", response_model=List[Dict[str, Any]])
# async def get_assignment_deadlines(
#     student_id: str = Query(None, description="Optional student ID to filter assignments"),
#     class_id: str = Query(None, description="Optional class ID to filter assignments"),
#     subject_id: str = Query(None, description="Optional subject ID to filter assignments"),
#     start_date: date = Query(None, description="Start date for filtering deadlines (YYYY-MM-DD)"),
#     end_date: date = Query(None, description="End date for filtering deadlines (YYYY-MM-DD)"),
# ) -> List[Dict[str, Any]]:
#     """
#     Fetches assignment deadlines from the simulated database.
#     Can be filtered by student_id, class_id, subject_id, and a date range.
#     """
#     filtered_assignments = []
#     for assignment in sample_assignments_db:
#         match = True
#         if student_id and "student_id" in assignment and assignment["student_id"] != student_id:
#             match = False
#         if class_id and assignment.get("class_id") != class_id:
#             match = False
#         if subject_id and assignment.get("subject_id") != subject_id:
#             match = False

#         assignment_deadline = datetime.strptime(assignment["deadline"], "%Y-%m-%d").date()
#         if start_date and assignment_deadline < start_date:
#             match = False
#         if end_date and assignment_deadline > end_date:
#             match = False

#         if match:
#             filtered_assignments.append(assignment)

#     if not filtered_assignments:
#         # In a real scenario, you might return an empty list or a 404 if no assignments match
#         # For this example, we'll return an empty list.
#         return []

#     return filtered_assignments

# To run this microservice:
# Navigate to the 'services/calendar' directory in your terminal
# Run: uvicorn app:app --host 127.0.0.1 --port 8007 --reload




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


# --- Database Configuration ---
# Replace with your actual MongoDB connection details
# MONGO_URI = "mongodb+srv://admin:1234@cluster0.ogyx0.mongodb.net/LMS?retryWrites=true&w=majority&appName=Cluster0" # Or from a config file
# DB_NAME = "LMS" # Replace with your actual database name

# client = MongoClient(MONGO_URI)
# db = client[DB_NAME]

# students_collection = db["student"]
# assignments_collection = db["assignment"]

# # --- API Endpoint ---

# @app.route("/calendar/student/<string:student_id>/assignments/deadlines", methods=["GET"])
# def get_student_assignment_deadlines(student_id):
#     """
#     Fetches assignment deadlines for a given student.
#     """
#     try:
#         # 1. Find the student and their registered subjects
#         student = students_collection.find_one({"student_id": student_id})

#         if not student:
#             return jsonify({"message": "Student not found"}), 404

#         registered_subjects = student.get("subject_id", [])

#         if not registered_subjects:
#             return jsonify({"message": "Student not registered for any subjects"}), 200

#         # 2. Find assignments for the registered subjects
#         # We use $in to match any subject_id in the registered_subjects array
#         assignments = assignments_collection.find(
#             {"subject_id": {"$in": registered_subjects}},
#             {"assignment_name": 1, "deadline": 1, "subject_id": 1} # Project only necessary fields
#         )

#         deadlines = []
#         for assignment in assignments:
#             deadlines.append({
#                 "assignment_id": assignment.get("assignment_id"), # Assuming assignment_id is present, but using .get for safety
#                 "assignment_name": assignment.get("assignment_name"),
#                 "deadline": assignment.get("deadline", {}).get("$date") if assignment.get("deadline") else None, # Extract $date
#                 "subject_id": assignment.get("subject_id")
#             })

#         return jsonify(deadlines), 200

#     except Exception as e:
#         app.logger.error(f"Error fetching assignment deadlines: {e}")
#         return jsonify({"message": "Internal server error"}), 500

# # You might have other routes and run configurations here
# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5002) # Or whatever port your calendar service runs on


# services/calendar/app/main.py (or app.py in your calendar microservice directory)

#----------------working api----------------------------
#-------------------------------------------------------

# from fastapi import FastAPI, HTTPException, Query, status
# from typing import List, Dict, Any, Optional
# from datetime import datetime, date
# from pymongo import MongoClient
# from pydantic import BaseModel

# app = FastAPI()

# # --- Database Configuration ---
# # IMPORTANT: Replace with your actual MongoDB connection details
# MONGO_URI = "mongodb+srv://admin:1234@cluster0.ogyx0.mongodb.net/LMS?retryWrites=true&w=majority&appName=Cluster0" # e.g., "mongodb://mongo:27017/" if using Docker Compose
# DB_NAME = "LMS" # e.g., "microservice_db"

# try:
#     client = MongoClient(MONGO_URI)
#     db = client[DB_NAME]
#     students_collection = db["student"]
#     assignments_collection = db["assignment"]
#     print(f"MongoDB connected successfully to database: {DB_NAME}")
# except Exception as e:
#     print(f"Error connecting to MongoDB: {e}")
#     # In a production environment, you might want more robust error handling,
#     # like retries or exiting the application if the DB connection is critical.
#     raise

# # --- Pydantic Response Model ---
# # This defines the structure of the data returned by your API
# class AssignmentDeadline(BaseModel):
#     assignment_id: Optional[str] = None
#     assignment_name: str
#     deadline: Optional[datetime] = None
#     subject_id: str

# # --- Core API Endpoint for Assignment Deadlines ---
# @app.get(
#     "/assignments/deadlines",
#     response_model=List[AssignmentDeadline],
#     summary="Fetch assignment deadlines for a student's registered subjects"
# )
# async def get_assignments_deadlines_for_student(
#     student_id: Optional[str] = Query(
#         None,
#         description="The ID of the student for whom to fetch assignment deadlines. "
#                     "If provided, deadlines will be filtered by subjects registered by this student."
#     ),
#     # Keep other parameters as optional, but note their interaction with student_id
#     class_id: Optional[str] = Query(None, description="Optional: Filter by a specific class ID."),
#     subject_id: Optional[str] = Query(None, description="Optional: Filter by a specific subject ID. "
#                                                          "If student_id is also provided, this will filter "
#                                                          "within the student's registered subjects."),
#     start_date: Optional[date] = Query(
#         None, description="Optional: Filter assignments with deadlines on or after this date (YYYY-MM-DD)."
#     ),
#     end_date: Optional[date] = Query(
#         None, description="Optional: Filter assignments with deadlines on or before this date (YYYY-MM-DD)."
#     )
# ) -> List[AssignmentDeadline]:
#     """
#     Retrieves a list of assignment deadlines.

#     **Primary Use Case:**
#     - If `student_id` is provided, it fetches all assignment deadlines for the subjects that
#       the specified student is registered for.

#     **Secondary Filters (can be combined with `student_id` or used independently):**
#     - `class_id`: Narrows down assignments to a specific class.
#     - `subject_id`: Narrows down assignments to a specific subject. If `student_id` is also
#       provided, this filters *within* the student's registered subjects.
#     - `start_date` / `end_date`: Filters assignments by their deadline date range.
#     """
#     query_filters = {}

#     # 1. Handle the student_id requirement first
#     if student_id:
#         student = students_collection.find_one({"student_id": student_id})
#         if not student:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail=f"Student with ID '{student_id}' not found."
#             )

#         registered_subjects = student.get("subject_id", [])
#         if not registered_subjects:
#             # Student exists but has no registered subjects, so no assignments to return
#             return []

#         # Add a filter to get assignments for any of the registered subjects
#         query_filters["subject_id"] = {"$in": registered_subjects}

#     # 2. Apply other filters, considering their interaction with student_id
#     if class_id:
#         query_filters["class_id"] = class_id

#     if subject_id:
#         # If student_id was provided, ensure this subject_id is part of their registered subjects
#         if student_id:
#             if subject_id not in registered_subjects: # registered_subjects from the student query above
#                 raise HTTPException(
#                     status_code=status.HTTP_400_BAD_REQUEST,
#                     detail=f"Subject '{subject_id}' is not registered by student '{student_id}'. "
#                             "Cannot filter deadlines for this subject."
#                 )
#             # If it is in registered_subjects, narrow the $in query to just this subject
#             # This effectively overrides the broader "$in": registered_subjects if a specific subject is also asked for.
#             query_filters["subject_id"] = subject_id
#         else:
#             # If no student_id, just filter by the provided subject_id
#             query_filters["subject_id"] = subject_id

#     # 3. Apply date range filters
#     if start_date or end_date:
#         deadline_query = {}
#         if start_date:
#             # Convert date to datetime at start of day for accurate comparison
#             deadline_query["$gte"] = datetime.combine(start_date, datetime.min.time())
#         if end_date:
#             # Convert date to datetime at end of day for accurate comparison
#             deadline_query["$lte"] = datetime.combine(end_date, datetime.max.time())
#         query_filters["deadline"] = deadline_query

#     # 4. Fetch assignments from the 'assignment' collection
#     projection = {
#         "assignment_id": 1,
#         "assignment_name": 1,
#         "deadline": 1,
#         "subject_id": 1,
#         "_id": 0 # Exclude default _id
#     }

#     try:
#         assignments_cursor = assignments_collection.find(query_filters, projection)

#         deadlines_list = []
#         for assignment in assignments_cursor:
#             # Handle potential {"$date": "..."} format if PyMongo doesn't auto-convert to datetime
#             deadline_val = assignment.get("deadline")
#             if isinstance(deadline_val, dict) and "$date" in deadline_val:
#                 try:
#                     # Convert ISO string (e.g., "2025-08-30T23:59:00.000Z") to datetime object
#                     deadline_val = datetime.fromisoformat(deadline_val["$date"].replace('Z', '+00:00'))
#                 except ValueError:
#                     # Fallback if parsing fails
#                     deadline_val = None
            
#             deadlines_list.append(AssignmentDeadline(
#                 assignment_id=assignment.get("assignment_id"),
#                 assignment_name=assignment.get("assignment_name"),
#                 deadline=deadline_val,
#                 subject_id=assignment.get("subject_id")
#             ))
        
#         return deadlines_list

#     except Exception as e:
#         print(f"An error occurred while fetching assignments: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Internal server error: {str(e)}"
#         )

# # Optional: Health check endpoint for the calendar microservice itself
# @app.get("/health", summary="Health check for Calendar Service")
# async def health_check():
#     try:
#         # Ping the database to check connectivity
#         client.admin.command('ping')
#         return {"status": "ok", "message": "Calendar service is healthy and connected to MongoDB."}
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to connect to MongoDB: {e}"
#         )

#-------------------------------------------------------------
#----------------End of working api----------------------------      




# services/calendar/app/main.py

from fastapi import FastAPI, HTTPException, Query, status
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from pymongo import MongoClient
from pydantic import BaseModel

app = FastAPI()

# --- Database Configuration ---
# IMPORTANT: Replace with your actual MongoDB connection details
MONGO_URI = "mongodb+srv://admin:1234@cluster0.ogyx0.mongodb.net/LMS?retryWrites=true&w=majority&appName=Cluster0" # e.g., "mongodb://mongo:27017/" if using Docker Compose
DB_NAME = "LMS" # e.g., "microservice_db"

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
    # Add teacher_id to the response model as teachers will create these
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