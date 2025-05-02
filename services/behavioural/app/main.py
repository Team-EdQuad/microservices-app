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


# Include the router
app.include_router(router)
