from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta,timezone
from pymongo.collection import Collection
from typing import Dict
from bson.son import SON
from .services.database import db  
from .services.predict_active_time import router as predict_router
import traceback

app = FastAPI(title="Behavioral Analysis API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Allow your frontend origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

router = APIRouter()
collection = db["behavioral_analysis"]


def get_current_week_range():
    today = datetime.utcnow()
    start_of_week = today - timedelta(days=today.weekday())  # Monday
    end_of_week = start_of_week + timedelta(days=7)          # Next Monday (exclusive end)
    
    return start_of_week.isoformat() + "Z", end_of_week.isoformat() + "Z"


@router.get("/TimeSpendOnResources/{subject_id}/{class_id}")
async def get_avg_time_spent(subject_id: str, class_id: str):
    start_date, end_date = get_current_week_range()

    pipeline = [
        {
            "$match": {
                "subject_id": subject_id,
                "class_id": class_id,
                "accessBeginTime": {
                    "$gte": start_date,
                    "$lt": end_date
                },
                "durationMinutes": { "$exists": True, "$ne": None }
            }
        },
        {
            "$group": {
                "_id": "$student_id",
                "totalDuration": { "$sum": "$durationMinutes" }
            }
        },
        {
            "$group": {
                "_id": None,
                "avgDuration": { "$avg": "$totalDuration" }
            }
        },
        {
            "$project": {
                "_id": 0,
                "avgTimeSpentPerStudent": "$avgDuration"
            }
        }
    ]

    try:
        result = list(db["behavioral_analysis"].aggregate(pipeline))

        #  New line: Fetch total students in the class from the students collection
        total_students = db["student"].count_documents({"class_id": class_id})

        if not result:
            return {
                "avgTimeSpentPerStudent": 0,
                "totalStudents": total_students
            }

        return {
            **result[0],
            "totalStudents": total_students
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.get("/SiteAverageActiveTime/{class_id}")
async def get_site_average_active_time(class_id: str):
    try:
        # Step 1: Get list of student_ids in the class
        students = list(db["student"].find({"class_id": class_id}))

        student_ids = [student["student_id"] for student in students]
        total_students = len(student_ids)

        if total_students == 0:
            raise HTTPException(status_code=404, detail="No students found for this class.")

        # Step 2: Define week range
        start_date, end_date = get_current_week_range()

        # Step 3: Aggregate total active time per student
        pipeline = [
            {
                "$match": {
                    "class_id": class_id,
                    "student_id": {"$in": student_ids},
                    "loginTime": {"$gte": start_date, "$lt": end_date},
                    "logoutTime": {"$exists": True, "$ne": None}
                }
            },
            {
                "$project": {
                    "student_id": 1,
                    "activeMinutes": {
                        "$divide": [
                            {"$subtract": [
                                {"$toDate": "$logoutTime"},
                                {"$toDate": "$loginTime"}
                            ]},
                            1000 * 60  # Convert ms to minutes
                        ]
                    }
                }
            },
            {
                "$group": {
                    "_id": "$student_id",
                    "totalActiveMinutes": {"$sum": "$activeMinutes"}
                }
            }
        ]

        result = list(db["site_activity_logs"].aggregate(pipeline))

        # Step 4: Build a map of active minutes per student
        active_map = {r["_id"]: r["totalActiveMinutes"] for r in result}

        # Step 5: Sum total minutes, fill 0 for students with no logins
        total_active_time = 0
        for sid in student_ids:
            total_active_time += active_map.get(sid, 0)

        # Step 6: Calculate average
        average_active_time = round(total_active_time / total_students, 2)

        return {
            "siteAverageActiveTimePerStudent": average_active_time,
            "totalStudents": total_students
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.get("/ResourceAccessFrequency/{subject_id}/{class_id}")
async def get_resource_access_frequency(subject_id: str, class_id: str):
    """
    Returns:
    - Access count per student
    - Access count per content
    - Total access count
    - Unique students (who accessed)
    - Average access per student (based on total class strength)
    """
    start_date, end_date = get_current_week_range()

    try:
        collection = db["behavioral_analysis"]

        # 1. Get total number of students in the class
        students = list(db["student"].find({"class_id": class_id}))
        total_students = len(students)

        if total_students == 0:
            raise HTTPException(status_code=404, detail="No students found in the given class.")

        # 2. Group by student
        student_pipeline = [
            {
                "$match": {
                    "subject_id": subject_id,
                    "class_id": class_id,
                    "accessBeginTime": { "$gte": start_date, "$lt": end_date },
                    "accessCount": { "$exists": True, "$ne": None }
                }
            },
            {
                "$group": {
                    "_id": "$student_id",
                    "accessCount": { "$sum": "$accessCount" }
                }
            }
        ]

        # 3. Group by content
        content_pipeline = [
            {
                "$match": {
                    "subject_id": subject_id,
                    "class_id": class_id,
                    "accessBeginTime": { "$gte": start_date, "$lt": end_date },
                    "accessCount": { "$exists": True, "$ne": None }
                }
            },
            {
                "$group": {
                    "_id": "$content_id",
                    "accessCount": { "$sum": "$accessCount" }
                }
            }
        ]

        student_accesses = list(collection.aggregate(student_pipeline))
        content_accesses = list(collection.aggregate(content_pipeline))

        if not student_accesses and not content_accesses:
            raise HTTPException(status_code=404, detail="No access data found for the given subject and class this week.")

        total_access_count = sum([s["accessCount"] for s in student_accesses])
        unique_students = len(student_accesses)
        avg_access_per_student = round(total_access_count / total_students, 2)

        return {
            "studentAccesses": [
                { "studentId": s["_id"], "accessCount": s["accessCount"] }
                for s in student_accesses
            ],
            "contentAccesses": [
                { "contentId": c["_id"], "accessCount": c["accessCount"] }
                for c in content_accesses
            ],
            "totalAccessCount": total_access_count,
            "uniqueStudents": unique_students,
            "totalStudentsInClass": total_students,
            "avgAccessPerStudentInClass": avg_access_per_student
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")



@router.post("/startContentAccess")
async def start_content_access(request_data: Dict):
    try:
        # Extract data from request body with proper validation
        if not isinstance(request_data, dict):
            raise HTTPException(status_code=400, detail="Invalid request format. Expected a JSON object.")
        
        student_id = request_data.get("student_id")
        content_id = request_data.get("content_id")
        
        # Validate required fields
        if not student_id or not content_id:
            raise HTTPException(
                status_code=400, 
                detail="Missing required fields. 'student_id' and 'content_id' are required."
            )
        
        print(f"Processing request for student_id: {student_id}, content_id: {content_id}")
        
        # Debug: Print all collections to verify we're connecting to the right database
        collection_names = db.list_collection_names()
        print(f"Available collections: {collection_names}")
        
        # Fetch content with verbose error handling
        content_collection = db["content"]
        print(f"Querying content collection with filter: {{'content_id': '{content_id}'}}")
        
        # Debug: Get a sample document to verify the schema
        sample = content_collection.find_one()
        if sample:
            print(f"Sample content document structure: {sample}")
        
        content = content_collection.find_one({"content_id": content_id})
        
        if not content:
            print(f"No content found with content_id: {content_id}")
            # Try a broader search to debug
            all_content = list(content_collection.find({}, {"content_id": 1, "_id": 0}).limit(5))
            print(f"Available content_ids: {all_content}")
            raise HTTPException(status_code=404, detail=f"Content not found with content_id: {content_id}")
        
        print(f"Content found: {content}")
        
        # Extract required fields with proper error handling
        subject_id = content.get("subject_id")
        class_id = content.get("class_id")
        
        if not subject_id or not class_id:
            error_msg = f"Missing required fields in content document: subject_id={subject_id}, class_id={class_id}"
            print(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)
        
        # Get current time
        access_begin_time = datetime.utcnow().isoformat() + "Z"
        
        # Prepare the document with fields matching your behavioral_analysis collection
        log_document = {
            "student_id": student_id,
            "content_id": content_id,
            "subject_id": subject_id,
            "class_id": class_id,
            "accessBeginTime": access_begin_time,
            "accessCount": 1
        }
        
        print(f"Prepared log document: {log_document}")
        
        # Insert the document
        behavioral_collection = db["behavioral_analysis"]
        result = behavioral_collection.insert_one(log_document)
        
        if not result.inserted_id:
            raise HTTPException(status_code=500, detail="Failed to insert document")
        
        print(f"Document inserted with ID: {result.inserted_id}")
        
        # Return success response
        return {
            "status": "success",
            "message": "Content access started successfully",
            "record_id": str(result.inserted_id),
            "timestamp": access_begin_time
        }
        
    except HTTPException as he:
        # Re-raise HTTP exceptions
        raise he
    except Exception as e:
        # Log detailed error information
        import traceback
        error_detail = traceback.format_exc()
        print(f"Unexpected error in start_content_access: {error_detail}")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error: {str(e)}"
        )
    

@router.post("/closeContentAccess")
async def close_content_access(request_data: Dict):
    try:
        # Extract data from request body with proper validation
        if not isinstance(request_data, dict):
            raise HTTPException(status_code=400, detail="Invalid request format. Expected a JSON object.")
        
        student_id = request_data.get("student_id")
        content_id = request_data.get("content_id")
        
        # Validate required fields
        if not student_id or not content_id:
            raise HTTPException(
                status_code=400, 
                detail="Missing required fields. 'student_id' and 'content_id' are required."
            )
        
        print(f"Processing close request for student_id: {student_id}, content_id: {content_id}")
        
        # Fetch the ongoing access entry
        behavioral_collection = db["behavioral_analysis"]
        
        query = {
            "student_id": student_id,
            "content_id": content_id,
            "accessCount": 1,  # Ensure we are closing an active access
            "closeTime": {"$exists": False}  # Ensure that the close time is not already set
        }
        
        print(f"Searching for active session with query: {query}")
        ongoing_access = behavioral_collection.find_one(query)
        
        if not ongoing_access:
            print(f"No ongoing content access found for student {student_id} and content {content_id}")
            raise HTTPException(
                status_code=404, 
                detail="No active access found for the given student and content."
            )
        
        # Calculate the close time (current time) with UTC timezone
        now_utc = datetime.now(timezone.utc)
        close_time = now_utc.isoformat().replace('+00:00', 'Z')
        print(f"Close time: {close_time}")
        
        # Parse the access begin time from the document
        access_begin_str = ongoing_access["accessBeginTime"]
        print(f"Original access begin time: {access_begin_str}")
        
        # Convert string to datetime object with timezone handling
        try:
            # Method 1: Direct parsing with timezone
            if access_begin_str.endswith('Z'):
                # Remove 'Z' and make it explicitly UTC
                clean_time_str = access_begin_str[:-1]
                access_begin_time = datetime.fromisoformat(clean_time_str).replace(tzinfo=timezone.utc)
            else:
                # Try to parse with timezone if present
                access_begin_time = datetime.fromisoformat(access_begin_str)
                if access_begin_time.tzinfo is None:
                    # If no timezone, assume UTC
                    access_begin_time = access_begin_time.replace(tzinfo=timezone.utc)
                    
            print(f"Parsed access begin time: {access_begin_time}")
        except ValueError as ve:
            print(f"Error in standard parsing: {ve}")
            try:
                # Method 2: Alternative parsing 
                clean_time_str = access_begin_str.replace('Z', '')
                access_begin_time = datetime.strptime(clean_time_str, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
                print(f"Alternative parsed time: {access_begin_time}")
            except Exception as e2:
                print(f"Failed alternative parsing: {e2}")
                raise HTTPException(status_code=500, detail=f"Unable to parse datetime: {access_begin_str}")
        
        # Calculate the duration in minutes (both datetimes now have timezone info)
        duration_seconds = (now_utc - access_begin_time).total_seconds()
        duration_minutes = round(duration_seconds / 60, 2)
        print(f"Calculated duration in minutes: {duration_minutes}")
        
        # Update the document in the collection
        update_result = behavioral_collection.update_one(
            {"_id": ongoing_access["_id"]},
            {
                "$set": {
                    "closeTime": close_time,
                    "durationMinutes": duration_minutes
                }
            }
        )
        
        if update_result.modified_count == 0:
            print(f"Failed to update document. Matched count: {update_result.matched_count}")
            raise HTTPException(status_code=500, detail="Failed to update the content access entry.")
        
        print(f"Successfully updated content access. Modified count: {update_result.modified_count}")
        
        # Return success response with detailed information
        return {
            "status": "success",
            "message": "Content access closed successfully",
            "student_id": student_id,
            "content_id": content_id,
            "close_time": close_time,
            "duration_minutes": duration_minutes,
            "record_id": str(ongoing_access["_id"])
        }
        
    except HTTPException as he:
        # Re-raise HTTP exceptions
        raise he
    except Exception as e:
        # Log detailed error information
        error_detail = traceback.format_exc()
        print(f"Unexpected error in close_content_access: {error_detail}")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error: {str(e)}"
        )


app.include_router(predict_router, prefix="/api")




app.include_router(router)
