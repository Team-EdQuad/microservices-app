import sys
import os


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'services')))


from fastapi import FastAPI, HTTPException
#from services.nonacademic import get_all_sports, create_sport, get_all_clubs, create_club, filter_sports

import httpx 
from fastapi.responses import JSONResponse
from typing import List
from services.academic import get_subject_names,get_student_content,get_all_assignments



app = FastAPI(title="Microservices API Gateway") 

@app.get("/api/subject/{student_id}", response_model=List)
async def get_subjects(student_id: str):
    return await get_subject_names(student_id)


@app.get("/api/content/{student_id}/{subject_id}", response_model=List)
async def get_content(student_id: str, subject_id: str):
    return await get_student_content(student_id, subject_id)


@app.get("/api/assignments/{student_id}/{subject_id}")
async def get_assignments(student_id: str, subject_id: str):
   
    try:
        return await get_all_assignments(student_id, subject_id)
    except HTTPException as exc:
        raise exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(exc)}")

