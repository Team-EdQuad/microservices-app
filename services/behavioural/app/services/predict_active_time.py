from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import logging
import os
import pickle
from datetime import datetime
from typing import Optional
from .database import client




COLLECTION_NAME = "active_time_prediction"
DATABASE_NAME = "LMS"  # Define database name as a string


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create logger instance
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter()

# Initialize model and scaler
model = None
scaler = StandardScaler()
FEATURES = ["Weeknumber", "SpecialEventThisWeek", "ResourcesUploadedThisWeek"]

# Pickle file paths
script_dir = os.path.dirname(os.path.abspath(__file__))
MODEL_PICKLE_PATH = os.path.join(script_dir, "trained_model.pkl")
SCALER_PICKLE_PATH = os.path.join(script_dir, "scaler.pkl")
MODEL_INFO_PATH = os.path.join(script_dir, "model_info.pkl")

def save_model_and_scaler():
    """Save the trained model and scaler to pickle files"""
    try:
        # Save model
        with open(MODEL_PICKLE_PATH, 'wb') as f:
            pickle.dump(model, f)
        
        # Save scaler
        with open(SCALER_PICKLE_PATH, 'wb') as f:
            pickle.dump(scaler, f)
        
        # Save model metadata
        model_info = {
            "trained_at": datetime.now().isoformat(),
            "features": FEATURES,
            "model_type": "LinearRegression"
        }
        with open(MODEL_INFO_PATH, 'wb') as f:
            pickle.dump(model_info, f)
        
        logger.info("Model, scaler, and metadata saved to pickle files")
        return True
    except Exception as e:
        logger.error(f"Error saving model: {str(e)}")
        return False

def load_model_and_scaler():
    """Load model and scaler from pickle files if they exist"""
    global model, scaler
    try:
        if (os.path.exists(MODEL_PICKLE_PATH) and 
            os.path.exists(SCALER_PICKLE_PATH) and 
            os.path.exists(MODEL_INFO_PATH)):
            
            # Load model
            with open(MODEL_PICKLE_PATH, 'rb') as f:
                model = pickle.load(f)
            
            # Load scaler
            with open(SCALER_PICKLE_PATH, 'rb') as f:
                scaler = pickle.load(f)
            
            # Load model info
            with open(MODEL_INFO_PATH, 'rb') as f:
                model_info = pickle.load(f)
            
            logger.info(f"Model loaded from pickle files. Trained at: {model_info.get('trained_at', 'Unknown')}")
            return True, model_info
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
    return False, None

def train_model_from_csv():
    """Train model from CSV data"""
    global model, scaler
    
    try:
        # Load dataset
        csv_path = os.path.join(script_dir, "patterned_sample_data.csv")
        
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Dataset file not found at: {csv_path}")
        
        data = pd.read_csv(csv_path)
        logger.info(f"Successfully loaded dataset with {len(data)} rows")
        
        # Drop irrelevant columns if they exist
        columns_to_drop = ["Subject", "Class"]
        data = data.drop(columns=[col for col in columns_to_drop if col in data.columns], errors="ignore")
        
        # Verify target column
        if "TotalActiveTime" not in data.columns:
            raise ValueError(f"TotalActiveTime column is missing. Available columns: {list(data.columns)}")
        
        # Verify feature columns
        missing_features = [feature for feature in FEATURES if feature not in data.columns]
        if missing_features:
            raise ValueError(f"Missing required features: {missing_features}")
        
        # Prepare features and target
        X = data[FEATURES]
        y = data["TotalActiveTime"]
        
        if len(X) == 0:
            raise ValueError("Dataset is empty after processing")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = scaler.fit_transform(X_train)
        
        # Train Linear Regression
        model = LinearRegression()
        model.fit(X_train_scaled, y_train)
        
        # Calculate training score
        train_score = model.score(X_train_scaled, y_train)
        logger.info(f"Model trained successfully with R² score: {train_score:.4f}")
        
        return True, train_score
        
    except Exception as e:
        logger.error(f"Error training model: {str(e)}")
        return False, str(e)

# Try to load existing model at startup
loaded, model_info = load_model_and_scaler()
if not loaded:
    logger.info("No existing model found, training new model...")
    success, result = train_model_from_csv()
    if success:
        save_model_and_scaler()

# Pydantic models
class PredictionInput(BaseModel):
    Weeknumber: int
    SpecialEventThisWeek: int
    ResourcesUploadedThisWeek: int
    
    class Config:
        schema_extra = {
            "example": {
                "Weeknumber": 25,
                "SpecialEventThisWeek": 1,
                "ResourcesUploadedThisWeek": 5
            }
        }

class PredictionOutput(BaseModel):
    predicted_active_time: float

class TrainingResponse(BaseModel):
    success: bool
    message: str
    training_score: Optional[float] = None
    trained_at: Optional[str] = None

class ModelStatus(BaseModel):
    model_loaded: bool
    model_info: Optional[dict] = None
    pickle_files_exist: bool


# Corrected visualization endpoint
@router.get("/visualize_data/{subject_id}/{class_id}")
async def visualize_data(subject_id: str, class_id: str):
    """Return x and y axis arrays for visualization filtered by subject_id and class_id"""
    try:
        # Use string "LMS" not variable LMS
        db = client["LMS"]  # Or use db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        
        # Query filtered data
        query = {"subject_id": subject_id, "class_id": class_id}
        cursor = collection.find(query).sort("Weeknumber", 1)
        
        x_values = []  # Weeknumber
        y_values = []  # TotalActiveTime
        
        for document in cursor:
            x_values.append(document["Weeknumber"])
            y_values.append(document["TotalActiveTime"])
        
        return {"x": x_values, "y": y_values}
        
    except Exception as e:
        logger.error(f"Visualization endpoint error: {str(e)}")
        return {"error": str(e)}



# Prediction endpoint
@router.post("/predict_active_time", response_model=PredictionOutput)
async def predict_active_time(input_data: PredictionInput):
    """Predict active time based on input features"""
    if model is None:
        raise HTTPException(
            status_code=500, 
            detail="Model is not initialized. Please train the model first using /train endpoint."
        )
    
    try:
        input_df = pd.DataFrame([input_data.dict()])
        input_scaled = scaler.transform(input_df[FEATURES])
        prediction = model.predict(input_scaled)[0]
        prediction = max(0, prediction)
        
        logger.info(f"Prediction made: {prediction} for input: {input_data.dict()}")
        return PredictionOutput(predicted_active_time=float(prediction))
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

# Training endpoint
@router.post("/train", response_model=TrainingResponse)
async def train_model_endpoint(background_tasks: BackgroundTasks):
    """Train a new model and save it as pickle files"""
    try:
        logger.info("Starting model training...")
        success, result = train_model_from_csv()
        
        if success:
            # Save model in background
            save_success = save_model_and_scaler()
            
            if save_success:
                return TrainingResponse(
                    success=True,
                    message="Model trained and saved successfully",
                    training_score=result,
                    trained_at=datetime.now().isoformat()
                )
            else:
                return TrainingResponse(
                    success=False,
                    message="Model trained but failed to save to pickle files",
                    training_score=result
                )
        else:
            return TrainingResponse(
                success=False,
                message=f"Training failed: {result}"
            )
            
    except Exception as e:
        logger.error(f"Training endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")

# Load model from pickle endpoint
@router.post("/load_model", response_model=TrainingResponse)
async def load_model_endpoint():
    """Load model from existing pickle files"""
    try:
        loaded, model_info = load_model_and_scaler()
        
        if loaded:
            return TrainingResponse(
                success=True,
                message="Model loaded successfully from pickle files",
                trained_at=model_info.get('trained_at') if model_info else None
            )
        else:
            return TrainingResponse(
                success=False,
                message="Failed to load model from pickle files. Files may not exist or be corrupted."
            )
            
    except Exception as e:
        logger.error(f"Load model endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to load model: {str(e)}")

# Model status endpoint
@router.get("/model_status", response_model=ModelStatus)
async def get_model_status():
    """Get current model status and information"""
    pickle_files_exist = (
        os.path.exists(MODEL_PICKLE_PATH) and 
        os.path.exists(SCALER_PICKLE_PATH) and 
        os.path.exists(MODEL_INFO_PATH)
    )
    
    model_info_data = None
    if pickle_files_exist:
        try:
            with open(MODEL_INFO_PATH, 'rb') as f:
                model_info_data = pickle.load(f)
        except:
            pass
    
    return ModelStatus(
        model_loaded=model is not None,
        model_info=model_info_data,
        pickle_files_exist=pickle_files_exist
    )

# Health check endpoint
@router.get("/health")
async def health_check():
    """Check if the service is healthy"""
    return {
        "status": "healthy" if model is not None else "model_not_loaded",
        "model_loaded": model is not None,
        "features": FEATURES,
        "endpoints": [
            "/predict_active_time",
            "/train", 
            "/load_model",
            "/model_status",
            "/health"
        ]
    }
