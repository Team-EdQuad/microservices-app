from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .services import academic_student, academic_teacher
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))


app = FastAPI(title="Academic API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(academic_student.router, tags=["Endpoints student"])
app.include_router(academic_teacher.router, tags=["Endpoints teacher"])

@app.get("/")
async def homepage():
    return {"message": "Welcome to the Academic API"}
