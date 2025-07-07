from typing import Dict, Any
from datetime import datetime
from app.utils.mongodb_connection import calendar_events

async def store_calendar_event(event_data: Dict[str, Any]):
    """
    Store a calendar event in MongoDB.
    
    Args:
        event_data (Dict[str, Any]): Calendar event data containing class_id, subject_id, date, and features
        
    Returns:
        InsertOneResult: Result of the MongoDB insert operation
    """
    # Validate required fields
    required_fields = ["class_id", "subject_id", "date", "features"]
    for field in required_fields:
        if field not in event_data:
            raise ValueError(f"Missing required field: {field}")
            
    # Validate features structure
    required_features = ["is_exam_week", "is_event_day", "is_school_day"]
    for feature in required_features:
        if feature not in event_data["features"]:
            raise ValueError(f"Missing required feature: {feature}")
            
    # Validate date format
    try:
        datetime.strptime(event_data["date"], "%Y-%m-%d")
    except ValueError:
        raise ValueError("Invalid date format. Use YYYY-MM-DD")
        
    
    # Insert the calendar event
    result = await calendar_events.insert_one(event_data)
    
    return result 