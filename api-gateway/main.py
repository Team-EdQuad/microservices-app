import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))




from fastapi import FastAPI, HTTPException
#from services.nonacademic import get_all_sports, create_sport, get_all_clubs, create_club, filter_sports
from service.academic import get_subject_names
import httpx 
from fastapi.responses import JSONResponse
from typing import List
from services.academic.app.models.academic import SubjectResponse


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

# NON_ACADEMIC_SERVICE_URL = "http://127.0.0.1:8003" 
# @app.get("/item/nonacademic/{item_id}")
# async def get_nonacademic_item(item_id: int):
#     try:
#         async with httpx.AsyncClient() as client:
#             # Add trailing slash if the Non-Academic service requires it
#             response = await client.get(f"{NON_ACADEMIC_SERVICE_URL}/item/nonacademic/{item_id}")
#             response.raise_for_status()  # Ensure HTTP errors are raised
#             return response.json()
#     except httpx.HTTPStatusError as exc:
#         raise HTTPException(status_code=exc.response.status_code, detail=str(exc))
#     except Exception as exc:
#         raise HTTPException(status_code=500, detail=f"Error fetching item {item_id}: {str(exc)}")




ACADEMIC_SERVICE_URL = "http://127.0.0.1:8002"

@app.get("/subject/{student_id}", response_model=List[SubjectResponse])
async def get_subjects(student_id: str):
    return await get_subject_names(student_id)





# TEST_SERVICE_URL = "http://127.0.0.1:8002" 

# @app.get("/api/item/{item_id}")
# async def get_nonacademic_item(item_id: int):
#     try:
#         async with httpx.AsyncClient() as client:
#             # Add trailing slash if the Non-Academic service requires it
#             response = await client.get(f"{TEST_SERVICE_URL}/item/{item_id}")
#             response.raise_for_status()  # Ensure HTTP errors are raised
#             return response.json()
#     except httpx.HTTPStatusError as exc:
#         raise HTTPException(status_code=exc.response.status_code, detail=str(exc))
#     except Exception as exc:
#         raise HTTPException(status_code=500, detail=f"Error fetching item {item_id}: {str(exc)}")

