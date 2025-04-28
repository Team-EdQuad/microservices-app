from fastapi import FastAPI, APIRouter
from .services import academic_student, academic_teacher

import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini AI
genai.configure(api_key=API_KEY)

# Initialize FastAPI app and router
app = FastAPI(title="Academic API")
router = APIRouter()

# Include routers for student and teacher endpoints
app.include_router(academic_student.router, tags=["Endpoints student"])
app.include_router(academic_teacher.router, tags=["Endpoints teacher"])

# Define a root endpoint
@app.get("/")
async def homepage():
    return {"message": "Welcome to the Academic API"}

# Include the router
app.include_router(router)












# from fastapi import FastAPI, APIRouter
# from ..services import academic_student, academic_teacher

# import os
# import google.generativeai as genai
# from dotenv import load_dotenv


# load_dotenv()
# API_KEY = os.getenv("GEMINI_API_KEY")

# # Configure Gemini AI
# genai.configure(api_key=API_KEY)

# app = FastAPI()
# router = APIRouter()

# app.include_router(academic_student.router, tags=["Endpoints student"])


# app.include_router(academic_teacher.router, tags=["Endpoints teacher"])


# @app.get("/")
# async def homepage():
#     return {"message": "welcome to the academic api"}


# app.include_router(router)
