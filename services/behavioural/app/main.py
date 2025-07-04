from fastapi import FastAPI, APIRouter, HTTPException, logger
from fastapi.middleware.cors import CORSMiddleware
from fastapi import status
from datetime import datetime, timedelta, timezone
import pytz  
from pymongo.collection import Collection
from typing import Dict
from .services.database import db  
from .services.predict_active_time import router as predict_router
import traceback
import logging
from .models.Behavioral import UpdateResponse


logger = logging.getLogger(__name__)
SRI_LANKA_TZ = pytz.timezone('Asia/Colombo')
app = FastAPI(title="Behavioral Analysis API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter()
collection = db["behavioral_analysis"]

def get_current_week_range():
    now = datetime.now(SRI_LANKA_TZ)
    start_of_week = now - timedelta(days=now.weekday())
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_week = start_of_week + timedelta(days=7)
    
    # Debug output
    print(f"Today: {now.strftime('%A, %B %d, %Y')}")
    print(f"Monday of this week: {start_of_week.strftime('%A, %B %d, %Y')}")
    
    start_utc = start_of_week.astimezone(timezone.utc)
    end_utc = end_of_week.astimezone(timezone.utc)
    
    return start_utc, end_utc

@router.get("/TimeSpendOnResources/{subject_id}/{class_id}")
async def get_avg_time_spent(subject_id: str, class_id: str):
    try:
        start_date, end_date = get_current_week_range()
        
        # Convert dates to string format for comparison with stored string dates
        start_date_str = start_date.isoformat().replace('+00:00', 'Z')
        end_date_str = end_date.isoformat().replace('+00:00', 'Z')

        pipeline = [
            {
                "$match": {
                    "subject_id": subject_id,
                    "class_id": class_id,
                    "accessBeginTime": {
                        "$gte": start_date_str,
                        "$lt": end_date_str
                    },
                    "durationMinutes": {"$exists": True, "$ne": None}
                }
            },
            {
                "$group": {
                    "_id": "$student_id",
                    "totalDuration": {"$sum": "$durationMinutes"}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "avgDuration": {"$avg": "$totalDuration"}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "avgTimeSpentPerStudent": "$avgDuration"
                }
            }
        ]

        result = list(db["behavioral_analysis"].aggregate(pipeline))
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
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")




@router.get("/SiteAverageActiveTime/{class_id}")
async def get_site_average_active_time(class_id: str):
    try:
        # Get registered students count in the class
        registered_students = list(db["student"].find({"class_id": class_id}))
        total_registered = len(registered_students)

        # Get current week range
        start_date, end_date = get_current_week_range()
        start_date_str = start_date.isoformat().replace('+00:00', 'Z')
        end_date_str = end_date.isoformat().replace('+00:00', 'Z')

        print(f"Query range: {start_date_str} to {end_date_str}")

        # Aggregation with lookup to match students in the given class
        pipeline = [
            {
                "$match": {
                    "loginTime": {"$gte": start_date_str, "$lt": end_date_str},
                    "logoutTime": {"$exists": True, "$ne": None}
                }
            },
            {
                "$lookup": {
                    "from": "student",
                    "localField": "student_id",
                    "foreignField": "student_id",
                    "as": "student_info"
                }
            },
            {
                "$unwind": "$student_info"
            },
            {
                "$match": {
                    "student_info.class_id": class_id
                }
            },
            {
                "$addFields": {
                    "loginTimeDate": {"$dateFromString": {"dateString": "$loginTime"}},
                    "logoutTimeDate": {"$dateFromString": {"dateString": "$logoutTime"}}
                }
            },
            {
                "$project": {
                    "student_id": 1,
                    "duration": {"$subtract": ["$logoutTimeDate", "$loginTimeDate"]}
                }
            },
            {
                "$group": {
                    "_id": "$student_id",
                    "totalMillis": {"$sum": "$duration"}
                }
            }
        ]

        result = list(db["student_login_details"].aggregate(pipeline))
        print(f"Aggregation result: {result}")

        if not result:
            return {
                "siteAverageActiveTimePerStudent": 0,
                "totalStudents": total_registered,
                "activeStudents": 0
            }

        # Calculate average time (in minutes)
        total_minutes = sum(doc["totalMillis"] / (1000 * 60) for doc in result)
        active_student_count = len(result)

        # Average per registered student
        divisor = max(total_registered, active_student_count)
        average = round(total_minutes / divisor, 2) if divisor > 0 else 0

        return {
            "siteAverageActiveTimePerStudent": average,
            "totalStudents": total_registered,
            "activeStudents": active_student_count
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))




@router.get("/ResourceAccessFrequency/{subject_id}/{class_id}")
async def get_resource_access_frequency(subject_id: str, class_id: str):
    try:
        start_date, end_date = get_current_week_range()
        start_date_str = start_date.isoformat().replace('+00:00', 'Z')
        end_date_str = end_date.isoformat().replace('+00:00', 'Z')

        collection = db["behavioral_analysis"]

        # Get total number of students in the class
        students = list(db["student"].find({"class_id": class_id}))
        total_students = len(students)

        if total_students == 0:
            raise HTTPException(status_code=404, detail="No students found in the given class.")

        # Group by student
        student_pipeline = [
            {
                "$match": {
                    "subject_id": subject_id,
                    "class_id": class_id,
                    "accessBeginTime": {"$gte": start_date_str, "$lt": end_date_str},
                    "accessCount": {"$exists": True, "$ne": None}
                }
            },
            {
                "$group": {
                    "_id": "$student_id",
                    "accessCount": {"$sum": "$accessCount"}
                }
            }
        ]

        # Group by content
        content_pipeline = [
            {
                "$match": {
                    "subject_id": subject_id,
                    "class_id": class_id,
                    "accessBeginTime": {"$gte": start_date_str, "$lt": end_date_str},
                    "accessCount": {"$exists": True, "$ne": None}
                }
            },
            {
                "$group": {
                    "_id": "$content_id",
                    "accessCount": {"$sum": "$accessCount"}
                }
            }
        ]

        student_accesses = list(collection.aggregate(student_pipeline))
        content_accesses = list(collection.aggregate(content_pipeline))

        if not student_accesses and not content_accesses:
            return {
                "studentAccesses": [],
                "contentAccesses": [],
                "totalAccessCount": 0,
                "uniqueStudents": 0,
                "totalStudentsInClass": total_students,
                "avgAccessPerStudentInClass": 0
            }

        total_access_count = sum([s["accessCount"] for s in student_accesses])
        unique_students = len(student_accesses)
        avg_access_per_student = round(total_access_count / total_students, 2) if total_students > 0 else 0

        return {
            "studentAccesses": [
                {"studentId": s["_id"], "accessCount": s["accessCount"]}
                for s in student_accesses
            ],
            "contentAccesses": [
                {"contentId": c["_id"], "accessCount": c["accessCount"]}
                for c in content_accesses
            ],
            "totalAccessCount": total_access_count,
            "uniqueStudents": unique_students,
            "totalStudentsInClass": total_students,
            "avgAccessPerStudentInClass": avg_access_per_student
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.post("/startContentAccess")
async def start_content_access(request_data: Dict):
    try:
        if not isinstance(request_data, dict):
            raise HTTPException(status_code=400, detail="Invalid request format. Expected a JSON object.")
        
        student_id = request_data.get("student_id")
        content_id = request_data.get("content_id")
        
        if not student_id or not content_id:
            raise HTTPException(
                status_code=400, 
                detail="Missing required fields. 'student_id' and 'content_id' are required."
            )
        
        print(f"Processing request for student_id: {student_id}, content_id: {content_id}")
        
        content_collection = db["content"]
        content = content_collection.find_one({"content_id": content_id})
        
        if not content:
            print(f"No content found with content_id: {content_id}")
            raise HTTPException(status_code=404, detail=f"Content not found with content_id: {content_id}")
        
        subject_id = content.get("subject_id")
        class_id = content.get("class_id")
        
        if not subject_id or not class_id:
            raise HTTPException(status_code=500, detail="Missing required fields in content document")
        
        # Use consistent datetime format
        access_begin_time = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        
        log_document = {
            "student_id": student_id,
            "content_id": content_id,
            "subject_id": subject_id,
            "class_id": class_id,
            "accessBeginTime": access_begin_time,
            "accessCount": 1
        }
        
        behavioral_collection = db["behavioral_analysis"]
        result = behavioral_collection.insert_one(log_document)
        
        return {
            "status": "success",
            "message": "Content access started successfully",
            "record_id": str(result.inserted_id),
            "timestamp": access_begin_time
        }
        
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/closeContentAccess")
async def close_content_access(request_data: Dict):
    try:
        if not isinstance(request_data, dict):
            raise HTTPException(status_code=400, detail="Invalid request format. Expected a JSON object.")
        
        student_id = request_data.get("student_id")
        content_id = request_data.get("content_id")
        
        if not student_id or not content_id:
            raise HTTPException(
                status_code=400, 
                detail="Missing required fields. 'student_id' and 'content_id' are required."
            )
        
        behavioral_collection = db["behavioral_analysis"]
        
        query = {
            "student_id": student_id,
            "content_id": content_id,
            "accessCount": 1,
            "closeTime": {"$exists": False}
        }
        
        ongoing_access = behavioral_collection.find_one(query)
        
        if not ongoing_access:
            raise HTTPException(
                status_code=404, 
                detail="No active access found for the given student and content."
            )
        
        # Use consistent datetime format
        now_utc = datetime.now(timezone.utc)
        close_time = now_utc.isoformat().replace('+00:00', 'Z')
        
        # Parse access begin time
        access_begin_str = ongoing_access["accessBeginTime"]
        
        try:
            if access_begin_str.endswith('Z'):
                clean_time_str = access_begin_str[:-1]
                access_begin_time = datetime.fromisoformat(clean_time_str).replace(tzinfo=timezone.utc)
            else:
                access_begin_time = datetime.fromisoformat(access_begin_str)
                if access_begin_time.tzinfo is None:
                    access_begin_time = access_begin_time.replace(tzinfo=timezone.utc)
        except ValueError:
            clean_time_str = access_begin_str.replace('Z', '')
            access_begin_time = datetime.strptime(clean_time_str, "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=timezone.utc)
        
        # Calculate duration
        duration_seconds = (now_utc - access_begin_time).total_seconds()
        duration_minutes = round(duration_seconds / 60, 2)
        
        # Update document
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
            raise HTTPException(status_code=500, detail="Failed to update the content access entry.")
        
        return {
            "status": "success",
            "message": "Content access closed successfully",
            "student_id": student_id,
            "content_id": content_id,
            "close_time": close_time,
            "duration_minutes": duration_minutes,
            "record_id": str(ongoing_access["_id"])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post(
    "/update_weekly_data/{subject_id}/{class_id}",
    response_model=UpdateResponse
)
async def update_weekly_data(subject_id: str, class_id: str):
    try:
        # --- 1. Collections ---
        pred_coll: Collection = db["active_time_prediction"]
        behav_coll: Collection = db["behavioral_analysis"]
        asn_coll: Collection = db["assignment"]
        cont_coll: Collection = db["content"]

        # --- 2. Compute this week's UTC range (Mon 00:00 → next Mon 00:00) ---
        week_start, week_end = get_current_week_range()

        # --- 3. Check if we've already inserted **real** data for THIS week ---
        real_filter = {
            "subject_id": subject_id,
            "class_id": class_id,
            "WeekStartDate": week_start,
            "WeekEndDate": week_end,
            "data": "1"
        }
        real_entry = pred_coll.find_one(real_filter)

        if real_entry:
            # A real row already exists this week—reuse its Weeknumber
            current_week_number = real_entry["Weeknumber"]
        else:
            # First real call this week → bump from the last synthetic week
            last_synth = pred_coll.find_one(
                {
                    "subject_id": subject_id,
                    "class_id": class_id,
                    # exclude any real data
                    "data": {"$ne": "1"}
                },
                sort=[("Weeknumber", -1)]
            )
            last_week = last_synth["Weeknumber"] if last_synth else 0
            current_week_number = last_week + 1

        logger.info(f"Using Weeknumber={current_week_number} for real data "
                    f"(range {week_start} → {week_end})")

        # --- 4. Aggregate TotalActiveTime ---
        b_pipeline = [
            {"$match": {
                "subject_id": subject_id,
                "class_id": class_id,
                "accessBeginTime": {"$exists": True, "$type": "string"},
                "durationMinutes": {"$exists": True, "$type": "number"}
            }},
            {"$addFields": {
                "parsedAccessTime": {"$dateFromString": {"dateString": "$accessBeginTime"}}
            }},
            {"$match": {
                "parsedAccessTime": {"$gte": week_start, "$lt": week_end}
            }},
            {"$group": {"_id": None, "total": {"$sum": "$durationMinutes"}}}
        ]
        b_res = list(behav_coll.aggregate(b_pipeline))
        total_active = round(b_res[0]["total"], 2) if b_res else 0.0

        # --- 5. SpecialEventThisWeek (assignments) ---
        asn_count = asn_coll.count_documents({
            "subject_id": subject_id,
            "class_id": class_id,
            "created_at": {"$gte": week_start, "$lt": week_end}
        })
        special_event = 1 if asn_count > 0 else 0

        # --- 6. ResourcesUploadedThisWeek (content) ---
        c_pipeline = [
            {"$match": {
                "subject_id": subject_id,
                "class_id": class_id,
                "upload_date": {"$exists": True, "$type": "string"}
            }},
            {"$addFields": {
                "upload_dt": {"$dateFromString": {"dateString": "$upload_date"}}
            }},
            {"$match": {
                "upload_dt": {"$gte": week_start, "$lt": week_end}
            }},
            {"$count": "cnt"}
        ]
        c_res = list(cont_coll.aggregate(c_pipeline))
        resources_uploaded = c_res[0]["cnt"] if c_res else 0

        # --- 7. Build the upsert document ---
        doc = {
            "Weeknumber": current_week_number,
            "TotalActiveTime": total_active,
            "subject_id": subject_id,
            "class_id": class_id,
            "SpecialEventThisWeek": special_event,
            "ResourcesUploadedThisWeek": resources_uploaded,
            "WeekStartDate": week_start,
            "WeekEndDate": week_end,
            "data": "1"
        }

        # --- 8. Upsert it (create or update the same week) ---
        pred_coll.update_one(
            real_filter,        # matches existing real row or creates new one
            {"$set": doc},
            upsert=True
        )

        # Remove any internal _id before returning
        doc.pop("_id", None)

        return UpdateResponse(
            success=True,
            message="Real weekly data upserted successfully.",
            subject_id=subject_id,
            class_id=class_id,
            updated_week=current_week_number,
            calculated_data=doc
        )

    except Exception as e:
        logger.exception(f"Error upserting real weekly data for {subject_id}/{class_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )



app.include_router(router)
app.include_router(predict_router, tags=["Endpoints prediction "])
