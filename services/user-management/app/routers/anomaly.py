# from fastapi import APIRouter, Depends, Query, HTTPException
# from typing import Optional, List
# from app.db.database import get_database
# from app.services.auth_service import get_current_user
# from bson import ObjectId
# from fastapi.encoders import jsonable_encoder

# router = APIRouter()

# # @router.get("/anomaly-detection/results")
# # async def get_anomaly_results(
# #     username: Optional[str] = Query(None),
# #     role: Optional[str] = Query(None),
# #     current_user=Depends(get_current_user)
# # ):
# #     # ✅ Only allow admins to access
# #     if current_user.role != "admin":
# #         raise HTTPException(status_code=403, detail="Only admins can access anomaly results")

# #     db = get_database()
# #     query = {}

# #     if username:
# #         query["username"] = username
# #     if role:
# #         query["role"] = role

# #     cursor = db["login_anomaly_results"].find(query).sort("timestamp", -1)
# #     results = []
# #     async for doc in cursor:
# #         doc["_id"] = str(doc["_id"])  # Convert ObjectId to string for JSON serialization
# #         results.append(doc)

# #     return {"results": results}

# @router.get("/anomaly-detection/results")
# async def get_anomaly_results(
#     username: Optional[str] = Query(None),
#     role: Optional[str] = Query(None),
#     current_user=Depends(get_current_user)
# ):
#     # Only allow admins
#     if current_user.role != "admin":
#         raise HTTPException(status_code=403, detail="Only admins can access anomaly results")

#     db = get_database()
#     query = {}

#     if username:
#         query["username"] = username
#     if role:
#         query["role"] = role

#     cursor = db["login_anomaly_results"].find(query).sort("timestamp", -1)
#     results = []
#     async for doc in cursor:
#         doc["_id"] = str(doc["_id"])  # Convert ObjectId to string
#         results.append(doc)

#     return {"results": results}

from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional, List
from app.db.database import get_database
from app.services.auth_service import get_current_user
from bson import ObjectId
from fastapi.encoders import jsonable_encoder

router = APIRouter()

# Commented out block (ignore this)
# @router.get("/anomaly-detection/results")
# async def get_anomaly_results(...):
#     # ... (your commented out code) ...

@router.get("/anomaly-detection/results")
async def get_anomaly_results(
    username: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    current_user=Depends(get_current_user)
):
    # Only allow admins
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can access anomaly results")

    db = get_database()
    query = {}

    # --- ADD NEW DEBUG PRINTS HERE ---
    print(f"\n--- Backend Debug for /anomaly-detection/results ---")
    print(f"Received query parameters: username='{username}', role='{role}'")
    print(f"Current user from token: Email='{current_user.email}', Role='{current_user.role}'") # Assuming current_user has .id and .role attributes
    # Adjust above line if current_user is a dict: current_user.get('sub') and current_user.get('role')

    if username:
        query["username"] = username
    if role:
        query["role"] = role

    print(f"Constructed MongoDB query filters: {query}") # <-- This is key! See what exact query is formed

    try:
        cursor = db["login_anomaly_results"].find(query).sort("timestamp", -1)
        results = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])  # Convert ObjectId to string
            results.append(doc)

        print(f"Found {len(results)} results from MongoDB for query: {query}") # <-- How many did it find?
        print(f"Returning data (first 5 items): {results[:5]}") # See some actual data if any
        # --- END NEW DEBUG PRINTS ---

        return {"results": results}
    except Exception as e:
        print(f"ERROR: Exception occurred while fetching anomaly results: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch anomaly results due to an internal error.")