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
        logger.info(f"Raw data fetched: {len(data_list)} records")
        
        if len(data_list) < 6:
            raise ValueError(f"Insufficient data for training. Found {len(data_list)} records, require at least 6.")
            
        data = pd.DataFrame(data_list)
        logger.info(f"DataFrame created with {len(data)} rows")
        
        # 2. Data Cleaning and Type Conversion
        essential_cols = ['TotalActiveTime', 'SpecialEventThisWeek', 'ResourcesUploadedThisWeek', 'Weeknumber']
        
        # Check original data types and missing values
        logger.info("Original data info:")
        for col in essential_cols:
            if col in data.columns:
                logger.info(f"{col}: dtype={data[col].dtype}, null_count={data[col].isnull().sum()}, sample_values={data[col].head(3).tolist()}")
            else:
                logger.error(f"Missing column: {col}")
                raise ValueError(f"Required column '{col}' not found in data")
        
        # Clean and convert data types
        for col in essential_cols:
            if col in data.columns:
                # Convert to numeric, forcing errors to NaN
                data[col] = pd.to_numeric(data[col], errors='coerce')
                
        logger.info("After type conversion:")
        for col in essential_cols:
            logger.info(f"{col}: null_count={data[col].isnull().sum()}")
        
        # Remove rows with missing essential data
        data_clean = data.dropna(subset=essential_cols).copy()
        logger.info(f"After removing rows with missing essential data: {len(data_clean)} rows")
        
        if len(data_clean) < 6:
            raise ValueError(f"Insufficient clean data. Found {len(data_clean)} valid records after cleaning, require at least 6.")
        
        # Sort by Weeknumber again to ensure proper order
        data_clean = data_clean.sort_values('Weeknumber').reset_index(drop=True)
        
        # 3. Feature Engineering with better handling
        data_clean['PrevWeekActiveTime'] = data_clean['TotalActiveTime'].shift(1)
        data_clean['Prev2WeekActiveTime'] = data_clean['TotalActiveTime'].shift(2)
        
        # Use a smaller rolling window if we don't have enough data
        rolling_window = min(3, len(data_clean) - 2)  # Ensure we have at least some data left
        data_clean['RollingMean5'] = data_clean['TotalActiveTime'].shift(1).rolling(window=rolling_window, min_periods=1).mean()
        
        data_clean['InteractionTerm'] = data_clean['SpecialEventThisWeek'] * data_clean['ResourcesUploadedThisWeek']
        
        logger.info(f"After feature engineering, before final dropna: {len(data_clean)} rows")
        
        # Check for NaN values in features
        features_to_check = ['PrevWeekActiveTime', 'Prev2WeekActiveTime', 'RollingMean5', 'InteractionTerm', 'SpecialEventThisWeek', 'ResourcesUploadedThisWeek']
        for feature in features_to_check:
            nan_count = data_clean[feature].isnull().sum()
            logger.info(f"{feature}: {nan_count} NaN values")
        
        # Instead of dropping all NaN, fill them strategically
        # For lag features, we can only start from the appropriate row
        # Remove only the first 2 rows (due to Prev2WeekActiveTime)
        data_final = data_clean.iloc[2:].copy()
        
        # Fill any remaining NaN values in RollingMean5 with the previous week's value
        data_final['RollingMean5'] = data_final['RollingMean5'].fillna(data_final['PrevWeekActiveTime'])
        
        logger.info(f"Final data shape: {len(data_final)} rows")
        
        if len(data_final) < 3:
            raise ValueError(f"Insufficient data after feature engineering. Found {len(data_final)} valid records, require at least 3.")
        
        # Verify all required features are present
        missing_features = [f for f in FEATURES if f not in data_final.columns]
        if missing_features:
            raise ValueError(f"Missing required features: {missing_features}")
        
        X = data_final[FEATURES]
        y = data_final["TotalActiveTime"]
        
        # Final check for any remaining NaN values
        nan_in_features = X.isnull().sum().sum()
        nan_in_target = y.isnull().sum()
        
        if nan_in_features > 0 or nan_in_target > 0:
            logger.warning(f"Found {nan_in_features} NaN in features, {nan_in_target} NaN in target. Dropping these rows.")
            # Create a mask for rows without NaN
            mask = ~(X.isnull().any(axis=1) | y.isnull())
            X = X[mask]
            y = y[mask]
        
        logger.info(f"Final feature matrix shape: {X.shape}")
        logger.info(f"Final target vector shape: {y.shape}")
        
        if len(X) < 3:
            raise ValueError(f"Insufficient data after final cleaning. Found {len(X)} valid records, require at least 3.")
        
        # 4. Train the Model
        # Use train-test split only if we have enough data
        if len(X) < 5:
            X_train, y_train = X, y
            logger.warning(f"Small dataset ({len(X)} records). Using all data for training without test split.")
        else:
            # Ensure we have at least 1 sample for test
            test_size = max(1, int(len(X) * 0.2))
            test_size = min(test_size, len(X) - 1)  # Ensure at least 1 for training
            train_size = len(X) - test_size
            
            X_train, _, y_train, _ = train_test_split(X, y, train_size=train_size, random_state=42)
            logger.info(f"Using train-test split: {len(X_train)} train, {test_size} test")
        
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

@router.get("/visualize_data/{subject_id}/{class_id}")
async def visualize_data(subject_id: str, class_id: str):
    try:
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]

        # Query without data filter first
        query = {
            "subject_id": subject_id,
            "class_id": class_id
        }

        # Sort by Weeknumber
        cursor = collection.find(query).sort("Weeknumber", 1)

        x_values, y_values = [], []
        for document in cursor:
            # Check for data field with different possible names
            data_value = None
            if "data" in document:
                data_value = document["data"]
            elif " data" in document:
                data_value = document[" data"]
            
            # Only include if data field matches our criteria
            if data_value in ["1", 1]:
                weeknumber = document.get("Weeknumber")
                total_active_time = document.get("TotalActiveTime")
                
                if weeknumber is not None and total_active_time is not None:
                    x_values.append(weeknumber)
                    y_values.append(total_active_time)

        return {"x": x_values, "y": y_values}

    except Exception as e:
        logger.error(f"Visualization endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))





