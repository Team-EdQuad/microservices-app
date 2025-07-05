from fastapi import FastAPI, Depends, HTTPException, Request
from app.routers import login, add_admin, add_student, add_teacher, delete_user, edit_profile, update_password, admin_user_management,logout
from app.services.auth_service import get_current_user
from app.models.admin_model import AdminModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from jose import jwt
import logging

# --- NEW IMPORTS FOR ANOMALY DETECTION ---
from app.anomaly_detection.workers.anomaly_detector import LoginInput, detect_login_anomaly_logic, retrain_models
# Assuming your user-management's database connection is in app/db/database.py
from app.db.database import get_database # Import your MongoDB client
# --- END NEW IMPORTS ---
from app.routers import anomaly

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="User Management")

# CORS origins - specify your frontend URLs
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "*"  # Remove this in production for security
]

# CORS configuration - MUST be added before exception handlers
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Custom exception handler for validation errors (422)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle 422 Unprocessable Entity errors with CORS headers"""
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Credentials': 'true',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': '*',
    }
    
    # Log the validation error for debugging
    logger.error(f"Validation error: {exc.errors()}")
    
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "body": exc.body,
            "message": "Validation error - please check your request data",
            "type": "validation_error"
        },
        headers=headers
    )

# Custom exception handler for HTTP exceptions (401, 403, 404, etc.)
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions with CORS headers"""
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Credentials': 'true',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': '*',
    }
    
    # Log the HTTP error
    logger.error(f"HTTP error {exc.status_code}: {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status_code": exc.status_code,
            "type": "http_error"
        },
        headers=headers
    )

# Custom exception handler for FastAPI HTTPException
@app.exception_handler(HTTPException)
async def fastapi_http_exception_handler(request: Request, exc: HTTPException):
    """Handle FastAPI HTTP exceptions with CORS headers"""
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Credentials': 'true',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': '*',
    }
    
    logger.error(f"FastAPI HTTP error {exc.status_code}: {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status_code": exc.status_code,
            "type": "fastapi_http_error"
        },
        headers=headers
    )

# Custom exception handler for general exceptions (500)
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions with CORS headers"""
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Credentials': 'true',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': '*',
    }
    
    # Log the general error
    logger.error(f"General error: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": str(exc),
            "type": "internal_error"
        },
        headers=headers
    )

# Add OPTIONS handler for preflight requests
@app.options("/{full_path:path}")
async def options_handler(request: Request, full_path: str):
    """Handle preflight OPTIONS requests"""
    return JSONResponse(
        content={},
        headers={
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': '*',
        }
    )

# Include routers for each functionality
app.include_router(login.router)
app.include_router(logout.router)  
app.include_router(add_admin.router)
app.include_router(add_student.router)
app.include_router(add_teacher.router)
app.include_router(delete_user.router)  # Uncommented this
app.include_router(admin_user_management.router)
app.include_router(edit_profile.router)
app.include_router(update_password.router)
app.include_router(anomaly.router)



# --- NEW ANOMALY DETECTION ENDPOINT ---
@app.post("/anomaly-detection/detect-login-anomaly")
async def detect_login_anomaly_api(
    data: LoginInput,
    # This endpoint can be called by anyone as part of login flow, or by admin
    # current_user=Depends(get_current_user) # Uncomment if only authenticated users can trigger
):
    """
    Endpoint to detect login anomalies based on provided input data.
    This will save login attempts and anomaly results to MongoDB
    and trigger model retraining.
    """
    try:
        # Get the MongoDB database client
        db_client = get_database() # Assuming get_database_client returns the 'db' object

        # Trigger anomaly detection logic
        result = detect_login_anomaly_logic(data=data, db_client=db_client)

        # Trigger retraining in the background to avoid blocking the API response
        # NOTE: Frequent retraining can be very resource-intensive.
        # Consider a separate background worker or scheduled task for this in production.
        # BackgroundTasks are good for fire-and-forget, but won't handle failures.
        # background_tasks.add_task(retrain_models, db_client) # Uncomment if you want background retraining

        return result
    except Exception as e:
        logger.error(f"Error during anomaly detection: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error during anomaly detection process")
# --- END NEW ANOMALY DETECTION ENDPOINT ---

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "User Management API is running"}

# Profile endpoint with enhanced error handling
@app.get("/profile")
async def get_profile(current_user=Depends(get_current_user)):
    """Get full user profile with normalized user_id and full_name"""
    try:
        role = current_user.role.lower()

        id_field_map = {
            "admin": "admin_id",
            "teacher": "teacher_id",
            "student": "student_id"
        }

        id_field = id_field_map.get(role)
        if not id_field:
            raise HTTPException(status_code=400, detail="Invalid user role")

        user_id = getattr(current_user, id_field, None)
        if user_id is None:
            raise HTTPException(status_code=404, detail="User ID not found")

        # Fix full_name if missing or invalid
        full_name = getattr(current_user, "full_name", "").strip()
        if not full_name or full_name.lower() == "string":
            first = getattr(current_user, "first_name", "").strip()
            last = getattr(current_user, "last_name", "").strip()
            full_name = f"{first} {last}".strip()

        # Convert the full model to dict
        user_dict = current_user.dict()

        # Override normalized fields
        user_dict["user_id"] = user_id
        user_dict["full_name"] = full_name

        return user_dict

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile error: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving profile")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "User Management API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }
