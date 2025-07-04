from fastapi import APIRouter, HTTPException
router = APIRouter()

@router.get("/nonacademic/{item_id}")
async def get_nonacademic_item(item_id: int):
    return {"item_id": item_id, "description": "Non-academic item details"}