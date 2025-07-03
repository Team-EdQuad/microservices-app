from fastapi import APIRouter, HTTPException
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import logging
import os
import joblib
from datetime import datetime
from .database import client
from ..models.Behavioral import PredictionOutput,TrainingResponse,ModelStatus,PredictionInput

# --- Configuration ---
COLLECTION_NAME = "active_time_prediction"
DATABASE_NAME = "LMS"
script_dir = os.path.dirname(os.path.abspath(__file__))

# --- Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
router = APIRouter()

# Features list remains the same for the model's structure
FEATURES = [
    'SpecialEventThisWeek', 'ResourcesUploadedThisWeek', 'PrevWeekActiveTime',
    'Prev2WeekActiveTime', 'RollingMean5', 'InteractionTerm'
]

# --- Helper Function for Dynamic File Paths ---
def get_model_paths(subject_id: str, class_id: str):
    """Generates unique file paths for a model based on subject and class ID."""
    filename_base = f"model_{subject_id}_{class_id}"
    model_path = os.path.join(script_dir, f"{filename_base}.joblib")
    info_path = os.path.join(script_dir, f"{filename_base}_info.joblib")
    return model_path, info_path

# --- Core Model Functions (Updated for Multi-Model) ---
def save_model(model_to_save, subject_id: str, class_id: str):
    """Save a trained model and its metadata to specific files."""
    try:
        model_path, info_path = get_model_paths(subject_id, class_id)
        joblib.dump(model_to_save, model_path)
        
        model_info = {
            "trained_at": datetime.now().isoformat(),
            "features": FEATURES,
            "model_type": "LinearRegression",
            "subject_id": subject_id,
            "class_id": class_id
        }
        joblib.dump(model_info, info_path)
        logger.info(f"Model saved for subject '{subject_id}', class '{class_id}'")
        return True
    except Exception as e:
        logger.error(f"Error saving model for {subject_id}/{class_id}: {e}")
        return False

def load_model(subject_id: str, class_id: str):
    """Load a specific model and its metadata from joblib files."""
    try:
        model_path, info_path = get_model_paths(subject_id, class_id)
        if os.path.exists(model_path) and os.path.exists(info_path):
            model = joblib.load(model_path)
            model_info = joblib.load(info_path)
            logger.info(f"Model loaded for subject '{subject_id}', class '{class_id}'")
            return model, model_info
    except Exception as e:
        logger.error(f"Error loading model for {subject_id}/{class_id}: {e}")
    return None, None

def train_model_from_db(subject_id: str, class_id: str):
    """Train a model by fetching filtered data from MongoDB."""
    try:
        # 1. Fetch data from MongoDB
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        query = {"subject_id": subject_id, "class_id": class_id}
        
        # Sort by Weeknumber to ensure correct .shift() and .rolling() operations
        cursor = collection.find(query).sort("Weeknumber", 1)
        
        data_list = list(cursor)
        if len(data_list) < 10: # Need enough data for training and feature engineering
            raise ValueError(f"Insufficient data for training. Found {len(data_list)} records, require at least 10.")
            
        data = pd.DataFrame(data_list)
        logger.info(f"Fetched {len(data)} rows from DB for subject '{subject_id}', class '{class_id}'")

        # 2. Perform Feature Engineering
        data['PrevWeekActiveTime'] = data['TotalActiveTime'].shift(1)
        data['Prev2WeekActiveTime'] = data['TotalActiveTime'].shift(2)
        data['RollingMean5'] = data['TotalActiveTime'].shift(1).rolling(window=5).mean()
        data['InteractionTerm'] = data['SpecialEventThisWeek'] * data['ResourcesUploadedThisWeek']
        data = data.dropna().reset_index(drop=True)

        X = data[FEATURES]
        y = data["TotalActiveTime"]

        X_train, _, y_train, _ = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # 3. Train the Model
        model = LinearRegression()
        model.fit(X_train, y_train)
        train_score = model.score(X_train, y_train)
        
        logger.info(f"Model for {subject_id}/{class_id} trained with R² score: {train_score:.4f}")
        return model, train_score
        
    except Exception as e:
        logger.error(f"Error during model training for {subject_id}/{class_id}: {e}")
        return None, str(e)


# --- API Endpoints ---
@router.post("/train/{subject_id}/{class_id}", response_model=TrainingResponse)
async def train_model_endpoint(subject_id: str, class_id: str):
    """Train a new model for a specific subject and class using data from the database."""
    logger.info(f"Received training request for subject '{subject_id}', class '{class_id}'")
    
    # Train the model
    trained_model, result = train_model_from_db(subject_id, class_id)
    
    if trained_model:
        # Save the newly trained model
        if save_model(trained_model, subject_id, class_id):
            return TrainingResponse(
                success=True,
                message="Model trained and saved successfully.",
                training_score=result,
                trained_at=datetime.now().isoformat()
            )
        else:
             return TrainingResponse(success=False, message="Model trained but failed to save.")
    else:
        # Training failed
        return TrainingResponse(success=False, message=f"Training failed: {result}")

@router.post("/predict_active_time/{subject_id}/{class_id}", response_model=PredictionOutput)
async def predict_active_time(subject_id: str, class_id: str, input_data: PredictionInput):
    """
    Predicts active time. The backend will fetch historical data and engineer
    the required features before making a prediction.
    """
    # 1. Load the specific model for the given subject and class
    model, _ = load_model(subject_id, class_id)
    if model is None:
        raise HTTPException(
            status_code=404,
            detail=f"Model for subject '{subject_id}' and class '{class_id}' not found. Please train it first."
        )

    try:
        # 2. Fetch historical data from MongoDB to engineer features
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        query = {"subject_id": subject_id, "class_id": class_id}
        
        # Fetch the last 5 records, sorted by week, to ensure we have enough data for the rolling mean
        history_cursor = collection.find(query).sort("Weeknumber", -1).limit(5)
        
        history_df = pd.DataFrame(list(history_cursor))

        if len(history_df) < 2:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough historical data to make a prediction. At least 2 weeks of data are required."
            )

        # 3. Perform Feature Engineering in the Backend
        # Sort ascending to get time series in the correct order
        history_df = history_df.sort_values(by="Weeknumber", ascending=True)

        prev_week_active_time = history_df['TotalActiveTime'].iloc[-1]
        prev_2_week_active_time = history_df['TotalActiveTime'].iloc[-2]
        
        # Ensure rolling mean is calculated correctly even with fewer than 5 records
        rolling_mean_5 = history_df['TotalActiveTime'].rolling(window=5, min_periods=1).mean().iloc[-1]
        
        interaction_term = input_data.SpecialEventThisWeek * input_data.ResourcesUploadedThisWeek

        # 4. Assemble the full feature vector for the model
        features_for_prediction = {
            'SpecialEventThisWeek': input_data.SpecialEventThisWeek,
            'ResourcesUploadedThisWeek': input_data.ResourcesUploadedThisWeek,
            'PrevWeekActiveTime': prev_week_active_time,
            'Prev2WeekActiveTime': prev_2_week_active_time,
            'RollingMean5': rolling_mean_5,
            'InteractionTerm': interaction_term
        }
        
        # Create a DataFrame with columns in the exact order the model expects
        input_df = pd.DataFrame([features_for_prediction], columns=FEATURES)

        # 5. Make the prediction
        prediction = model.predict(input_df)[0]
        prediction = max(0, prediction)  # Ensure prediction is not negative

        return PredictionOutput(predicted_active_time=float(prediction))

    except Exception as e:
        logger.error(f"Prediction error for {subject_id}/{class_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@router.get("/model_status/{subject_id}/{class_id}", response_model=ModelStatus)
async def get_model_status(subject_id: str, class_id: str):
    """Get the status of a specific model."""
    _, model_info = load_model(subject_id, class_id)
    
    if model_info:
        return ModelStatus(model_exists=True, model_info=model_info)
    else:
        return ModelStatus(model_exists=False, model_info=None)

# The /visualize_data endpoint remains unchanged as it already supports filtering
@router.get("/visualize_data/{subject_id}/{class_id}")
async def visualize_data(subject_id: str, class_id: str):
    """Return x and y axis arrays for visualization filtered by subject_id and class_id"""
    try:
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        query = {"subject_id": subject_id, "class_id": class_id}
        cursor = collection.find(query).sort("Weeknumber", 1)
        x_values, y_values = [], []
        for document in cursor:
            x_values.append(document.get("Weeknumber"))
            y_values.append(document.get("TotalActiveTime"))
        return {"x": x_values, "y": y_values}
    except Exception as e:
        logger.error(f"Visualization endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))