import pandas as pd
import joblib
import os
from datetime import datetime, timedelta
from app.utils.mongodb_connection import calendar_events, attendance_store

# Load model and feature columns
BASE_DIR = os.path.dirname(__file__)
MODEL_DIR = os.path.join(BASE_DIR, "models")

model_path = os.path.join(MODEL_DIR, "attendance_predictor.pkl")
columns_path = os.path.join(MODEL_DIR, "feature_columns.pkl")

model = joblib.load(model_path)
feature_columns = joblib.load(columns_path)

async def predict_attendance(class_id: str, subject_id: str, target_date: datetime) -> dict:
    # Query relevant events ±7 days
    date_buffer_start = (target_date - timedelta(days=7)).strftime("%Y-%m-%d")
    date_buffer_end = (target_date + timedelta(days=7)).strftime("%Y-%m-%d")

    calendar_filter = {
        "class_id": class_id,
        "subject_id": subject_id,
        "date": {"$gte": date_buffer_start, "$lte": date_buffer_end}
    }

    cursor = calendar_events.find(calendar_filter)
    events = await cursor.to_list(length=None)

    if not events:
        raise ValueError("No calendar events found for this class, subject, and date.")

    # Parse event dates
    for event in events:
        event["date"] = datetime.strptime(event["date"], "%Y-%m-%d")

    # Filter events on target date
    events_today = [e for e in events if e["date"].date() == target_date.date()]

    # Check if school is closed on that day
    if events_today and events_today[0]["features"]["is_school_day"] == 0:
        return {
            "class_id": class_id,
            "subject_id": subject_id,
            "date": target_date.strftime("%Y-%m-%d"),
            "predicted_attendance_rate": -1,  # -1 indicates school is closed
            "features_used": {
                "is_event_day": events_today[0]["features"]["is_event_day"],
                "is_exam_week": events_today[0]["features"]["is_exam_week"],
                "is_school_day": events_today[0]["features"]["is_school_day"]
            }
        }

    # Calculate features
    days_until_next_holiday, days_since_last_holiday = calculate_holiday_distances(events, target_date)
    number_of_school_days_in_week = calculate_school_days_in_week(events, target_date)
    is_event_day = events_today[0]["features"]["is_event_day"] if events_today else 0
    is_exam_day = events_today[0]["features"]["is_exam_week"] if events_today else 0

    # Build feature dictionary
    features = {
        "weekday": target_date.strftime("%A"),
        "month": target_date.strftime("%B"),
        "class": class_id,
        "subject": subject_id,
        "year": target_date.year,
        "day": target_date.day,
        "number_of_school_days_in_week": number_of_school_days_in_week,
        "days_until_next_holiday": days_until_next_holiday,
        "days_since_last_holiday": days_since_last_holiday,
        "is_event_day": is_event_day,
        "is_exam_day": is_exam_day
    }

    # Predict attendance
    prediction = make_prediction(features)

    return {
        "class_id": class_id,
        "subject_id": subject_id,
        "date": target_date.strftime("%Y-%m-%d"),
        "predicted_attendance_rate": round(float(prediction), 2),
        "features_used": features
    }

def make_prediction(features: dict) -> float:
    input_df = pd.DataFrame([features])

    categorical_cols = ['weekday', 'month', 'class', 'subject']
    input_df_encoded = pd.get_dummies(input_df, columns=categorical_cols, drop_first=True)

    for col in feature_columns:
        if col not in input_df_encoded.columns:
            input_df_encoded[col] = 0

    input_df_encoded = input_df_encoded[feature_columns]

    prediction = model.predict(input_df_encoded)[0]
    return prediction

# Helper functions
def calculate_holiday_distances(events, current_date):
    days_until_next_holiday = float('inf')
    days_since_last_holiday = float('inf')

    for event in events:
        event_date = event["date"]
        is_holiday = event["features"]["is_school_day"] == 0

        if is_holiday:
            delta_days = (event_date - current_date).days
            if delta_days >= 0:
                days_until_next_holiday = min(days_until_next_holiday, delta_days)
            if delta_days < 0:
                days_since_last_holiday = min(days_since_last_holiday, abs(delta_days))

    days_until_next_holiday = days_until_next_holiday if days_until_next_holiday != float('inf') else 0
    days_since_last_holiday = days_since_last_holiday if days_since_last_holiday != float('inf') else 0

    return days_until_next_holiday, days_since_last_holiday

def calculate_school_days_in_week(events, current_date):
    year, week_num, _ = current_date.isocalendar()
    count = 0

    for event in events:
        event_date = event["date"]
        event_year, event_week_num, _ = event_date.isocalendar()
        if event_year == year and event_week_num == week_num and event["features"]["is_school_day"] == 1:
            count += 1

    return count

