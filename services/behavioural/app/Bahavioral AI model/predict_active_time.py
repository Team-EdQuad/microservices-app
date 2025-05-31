from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize model and scaler
model = None
scaler = StandardScaler()
FEATURES = ["Weeknumber", "SpecialEventThisWeek", "ResourcesUploadedThisWeek"]

# Train model
def train_model():
    global model
    try:
        # Load dataset
        data = pd.read_csv("patterned_sample_data.csv")
        
        # Drop irrelevant columns if they exist
        columns_to_drop = ["Subject", "Class"]
        data = data.drop(columns=[col for col in columns_to_drop if col in data.columns], errors="ignore")
        
        # Verify target column
        if "TotalActiveTime" not in data.columns:
            raise ValueError("TotalActiveTime column is missing in the dataset.")
        
        # Prepare features and target
        X = data[FEATURES]
        y = data["TotalActiveTime"]
        
        # Split data
        X_train, _, y_train, _ = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = scaler.fit_transform(X_train)
        
        # Train Linear Regression
        model = LinearRegression()
        model.fit(X_train_scaled, y_train)
        logger.info("Linear Regression model trained successfully")
    except FileNotFoundError:
        logger.error("Dataset file 'patterned_sample_data.csv' not found")
        return
    except Exception as e:
        logger.error(f"Error training model: {str(e)}")
        return

# Attempt to train model at startup
train_model()

# Pydantic model for request validation
class PredictionInput(BaseModel):
    Weeknumber: int
    SpecialEventThisWeek: int
    ResourcesUploadedThisWeek: int

# Pydantic model for response
class PredictionOutput(BaseModel):
    predicted_active_time: float

@router.post("/predict_active_time", response_model=PredictionOutput)
async def predict_active_time(input_data: PredictionInput):
    if model is None:
        raise HTTPException(status_code=500, detail="Model is not initialized. Ensure dataset is available.")
    
    try:
        # Convert input to DataFrame
        input_df = pd.DataFrame([input_data.dict()])
        
        # Verify required features
        if not all(col in input_df.columns for col in FEATURES):
            raise ValueError("Missing required features")
        
        # Scale input
        input_scaled = scaler.transform(input_df[FEATURES])
        
        # Predict
        prediction = model.predict(input_scaled)[0]
        
        # Ensure non-negative prediction
        prediction = max(0, prediction)
        
        return PredictionOutput(predicted_active_time=float(prediction))
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Prediction failed: {str(e)}")