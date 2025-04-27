from pydantic import BaseModel

class Sports(BaseModel):
    sport_id:str
    sport_name:str
    description:str
    location:str
    schedule: str
    type:str
    category:str


class Clubs(BaseModel):
    club_id: str
    club_name :str
    description : str
    location : str
    schedule: str
    