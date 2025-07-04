from fastapi import APIRouter, HTTPException
from .database import collection31, collection32
from ..schemas.nonacademic import all_sports, individual_sport, all_clubs, individual_club
from ..models.nonacademic import Sports,Clubs
from bson.objectid import ObjectId
from typing import List


sports_router = APIRouter()
clubs_router = APIRouter()

@sports_router.get("/", response_model=List[dict])
async def get_all_sports():
    data = list(collection31.find())
    return all_sports(data)

@sports_router.post("/", response_model=dict)
async def create_sport(sport: Sports):
    try:
        sport_dict = sport.model_dump()
        result = collection31.insert_one(sport_dict)
        created_sport = collection31.find_one({"_id": result.inserted_id})
        return individual_sport(created_sport)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating sport: {str(e)}")

    
@sports_router.get("/filter/" , response_model=List[dict])
async def filter_sports(type: str = None, category: str = None):
    try:
        query={}
        if type:
            query["type"] = type
        
        if category:
            query["category"] = category

        data = list(collection31.find(query))

        return all_sports(data)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail = f"Error filtering sports: {str(e)}")


@clubs_router.get("/", response_model = List[dict])
async def get_all_clubs():
    data = list(collection32.find())
    return all_clubs(data)


@clubs_router.post("/" , response_model=dict)
async def create_club(club: Clubs):
    try:
        club_dict = club.model_dump()
        result = collection32.insert_one(club_dict)
        created_club = collection32.find_one({"_id": result.inserted_id})
        return individual_club(created_club)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating club: {str(e)}")

# @student_dashboard_router.get("/{student_id}/{class_id}/assignments/filter", response_model=List[dict])

router = APIRouter()

@router.get("/nonacademic/{item_id}")
async def get_nonacademic_item(item_id: int):
    return {"item_id": item_id, "description": "Non-academic item details"}

