from fastapi import FastAPI, APIRouter, HTTPException
from datetime import datetime, timedelta
from pymongo.collection import Collection
from typing import Dict
from bson.son import SON
from .services.database import db

# Initialize FastAPI app and router
app = FastAPI(title="Behavioral Analysis API")
router = APIRouter()


def get_current_week_range():
    """Returns a hardcoded date range for testing (May 2025)."""
    start = datetime(2025, 5, 1)  # May 1, 2025 (Monday)
    end = start + timedelta(days=7)  # May 7, 2025 (Next Monday)
    
    # Convert to ISO 8601 string format for MongoDB comparison
    start_str = start.isoformat() + "Z"  # Adding 'Z' for UTC time zone
    end_str = end.isoformat() + "Z"  # Adding 'Z' for UTC time zone
    
    return start_str, end_str

# Endpoint to calculate average time spent on resources
@router.get("/TimeSpendOnResources/{subject_id}/{class_id}")
async def get_avg_time_spent(subject_id: str, class_id: str):
    """
    Calculate the average time spent on resources for a given subject and class.
    """
    start_date, end_date = get_current_week_range()

    # MongoDB aggregation pipeline
    pipeline = [
        {
            "$match": {
                "subjectId": subject_id,
                "classId": class_id,
                "accessBeginTime": {
                    "$gte": start_date,
                    "$lt": end_date
                },
                "durationMinutes": { "$exists": True, "$ne": None }  # Ensure 'durationMinutes' exists
            }
        },
        {
            "$group": {
                "_id": "$studentId",  # Group by studentId
                "totalDuration": { "$sum": "$durationMinutes" }  # Sum up the total duration for each student
            }
        },
        {
            "$group": {
                "_id": None,
                "avgDuration": { "$avg": "$totalDuration" },  # Calculate the average of total durations
                "studentCount": { "$sum": 1 }  # Count the number of students
            }
        },
        {
            "$project": {
                "_id": 0,
                "avgTimeSpentPerStudent": "$avgDuration",  # Field for average time spent per student
                "totalStudents": "$studentCount"  # Field for total number of students
            }
        }
    ]

    try:
        # Access the MongoDB collection directly
        result = list(db["behavioral_analysis"].aggregate(pipeline))  # Assuming db is already connected
        
        if not result:
            raise HTTPException(status_code=404, detail="No data found for the given subject and class this week.")
        
        return result[0]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


# Endpoint to get resource access frequency
@router.get("/ResourceAccessFrequency/{subject_id}/{class_id}")
async def get_resource_access_frequency(subject_id: str, class_id: str):
    """
    Returns:
    - Access count per student
    - Access count per content
    - Total access count and unique students
    """
    start_date, end_date = get_current_week_range()

    try:
        collection = db["behavioral_analysis"]

        # Group by student
        student_pipeline = [
            {
                "$match": {
                    "subjectId": subject_id,
                    "classId": class_id,
                    "accessBeginTime": { "$gte": start_date, "$lt": end_date },
                    "accessCount": { "$exists": True, "$ne": None }
                }
            },
            {
                "$group": {
                    "_id": "$studentId",
                    "accessCount": { "$sum": "$accessCount" }
                }
            }
        ]

        # Group by content
        content_pipeline = [
            {
                "$match": {
                    "subjectId": subject_id,
                    "classId": class_id,
                    "accessBeginTime": { "$gte": start_date, "$lt": end_date },
                    "accessCount": { "$exists": True, "$ne": None }
                }
            },
            {
                "$group": {
                    "_id": "$contentId",
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
            "uniqueStudents": unique_students
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


# Endpoint to calculate site average active time
@router.get("/SiteAverageActiveTime/{subject_id}/{class_id}")
async def get_site_average_active_time(subject_id: str, class_id: str):
    """
    Calculates the average site active time per session (in minutes)
    for a given subject and class within the current week.
    """
    start_date, end_date = get_current_week_range()

    pipeline = [
        {
            "$match": {
                "subjectId": subject_id,
                "classId": class_id,
                "loginTime": {
                    "$gte": start_date,
                    "$lt": end_date
                },
                "logoutTime": { "$exists": True, "$ne": None }
            }
        },
        {
            "$project": {
                "activeMinutes": {
                    "$divide": [
                        {
                            "$subtract": [
                                { "$toDate": "$logoutTime" },  # Convert logoutTime from string to Date
                                { "$toDate": "$loginTime" }    # Convert loginTime from string to Date
                            ]
                        },
                        1000 * 60  # Convert milliseconds to minutes
                    ]
                }
            }
        },
        {
            "$group": {
                "_id": None,
                "siteAverageActiveTime": { "$avg": "$activeMinutes" },
                "sessionCount": { "$sum": 1 }
            }
        },
        {
            "$project": {
                "_id": 0,
                "siteAverageActiveTime": { "$round": ["$siteAverageActiveTime", 2] },
                "sessionCount": 1
            }
        }
    ]

    try:
        result = list(db["site_activity_logs"].aggregate(pipeline))

        if not result:
            raise HTTPException(status_code=404, detail="No site activity data found for this subject and class this week.")

        return result[0]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")



# Include the router
app.include_router(router)
