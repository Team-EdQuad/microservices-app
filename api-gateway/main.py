import sys
import os


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'services')))


from fastapi import FastAPI, HTTPException
#from services.nonacademic import get_all_sports, create_sport, get_all_clubs, create_club, filter_sports

import httpx 
from fastapi.responses import JSONResponse
from typing import List
#from services.academic.app.models.academic import SubjectResponse
from services.academic import get_subject_names,get_student_content



app = FastAPI(title="Microservices API Gateway") 

# @app.get("/api/nonacademic/sports", response_model=list)
# async def fetch_all_sports():
#     return await get_all_sports()

# @app.post("/api/nonacademic/sports", response_model=dict)
# async def add_sport(sport: dict):
#     return await create_sport(sport)

# @app.get("/api/nonacademic/sports/filter", response_model=list)
# async def filter_sports_endpoint(type: str = None, category: str = None):
#     return await filter_sports(type, category)

# @app.get("/api/nonacademic/clubs", response_model=list)
# async def fetch_all_clubs():
#     return await get_all_clubs()

# @app.post("/api/nonacademic/clubs", response_model=dict)
# async def add_club(club: dict):
#     return await create_club(club)


@app.get("/api/subject/{student_id}", response_model=List)
async def get_subjects(student_id: str):
    return await get_subject_names(student_id)


@app.get("/api/content/{student_id}/{subject_id}", response_model=List)
async def get_content(student_id: str, subject_id: str):
    return await get_student_content(student_id, subject_id)

# @app.get("/api/subject/{student_id}", response_model=List)
# async def get_subjects(student_id: str):
#     return await get_subject_names(student_id)


# @app.get("/api/content/{student_id}/{subject_id}", response_model=List)
# async def get_content(student_id: str, subject_id: str):
#     return await get_content_details(student_id, subject_id)



