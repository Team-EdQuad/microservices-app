import httpx
from fastapi import HTTPException
import logging

from pydantic import BaseModel

BEHAVIOURAL_SERVICE_URL = "http://127.0.0.1:8005"


class PredictionInput(BaseModel):
    SpecialEventThisWeek: int
    ResourcesUploadedThisWeek: int

async def time_spent_on_resources(subject_id, class_id):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BEHAVIOURAL_SERVICE_URL}/TimeSpendOnResources/{subject_id}/{class_id}")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(exc)}")
    

async def average_active_time(class_id):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BEHAVIOURAL_SERVICE_URL}/SiteAverageActiveTime/{class_id}")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(exc)}")

async def resource_access_frequency(subject_id, class_id):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BEHAVIOURAL_SERVICE_URL}/ResourceAccessFrequency/{subject_id}/{class_id}")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(exc)}")

async def content_access_start(student_id, content_id):
    try:
        # Prepare the request payload as per the backend API expectations
        payload = {
            "student_id": student_id,
            "content_id": content_id
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BEHAVIOURAL_SERVICE_URL}/startContentAccess",
                json=payload
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        # Pass through the status code and error message from the backend
        error_detail = exc.response.json().get("detail", str(exc)) if exc.response.headers.get("content-type") == "application/json" else str(exc)
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except Exception as exc:
        logging.error(f"Unexpected error in content_access_start: {str(exc)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(exc)}")

async def content_access_close(student_id, content_id):
    try:
        # Prepare the request payload as per the backend API expectations
        payload = {
            "student_id": student_id,
            "content_id": content_id
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BEHAVIOURAL_SERVICE_URL}/closeContentAccess",
                json=payload
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        # Pass through the status code and error message from the backend
        error_detail = exc.response.json().get("detail", str(exc)) if exc.response.headers.get("content-type") == "application/json" else str(exc)
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except Exception as exc:
        logging.error(f"Unexpected error in content_access_close: {str(exc)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(exc)}")
    
async def Visualize_data_list(subject_id: str, class_id: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BEHAVIOURAL_SERVICE_URL}/visualize_data/{subject_id}/{class_id}")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(exc)}")


async def update_collection_active_time(subject_id: str, class_id: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{BEHAVIOURAL_SERVICE_URL}/update_weekly_data/{subject_id}/{class_id}")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(exc)}")



async def call_prediction_service(
    subject_id: str,
    class_id: str,
    input_data: PredictionInput
):
    """
    Calls the downstream ML prediction service.
    """
    # The URL for the ML service's specific prediction endpoint
    service_url = f"{BEHAVIOURAL_SERVICE_URL}/predict_active_time/{subject_id}/{class_id}"

    try:
        async with httpx.AsyncClient() as client:
            # Send the request with the input data as a JSON body
            response = await client.post(service_url, json=input_data.dict())
            
            # Raise an exception for bad status codes (4xx or 5xx)
            response.raise_for_status()
            
            # Return the JSON response from the ML service
            return response.json()
            
    except httpx.HTTPStatusError as exc:
        # Forward the error from the downstream service to the client
        raise HTTPException(
            status_code=exc.response.status_code, 
            detail=f"Error from prediction service: {exc.response.text}"
        )
    except httpx.RequestError as exc:
        # Handle network errors (e.g., the service is down)
        raise HTTPException(
            status_code=503, # Service Unavailable
            detail=f"Could not connect to the prediction service: {exc}"
        )
    except Exception as exc:
        # Handle other unexpected errors
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(exc)}")











async def model_train(subject_id, class_id):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{BEHAVIOURAL_SERVICE_URL}/train/{subject_id}/{class_id}")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Training error: {str(exc)}")


# async def load_model():
#     try:
#         async with httpx.AsyncClient() as client:
#             response = await client.post(f"{BEHAVIOURAL_SERVICE_URL}/load_model")
#             response.raise_for_status()
#             return response.json()
#     except httpx.HTTPStatusError as exc:
#         raise HTTPException(status_code=exc.response.status_code, detail=str(exc))
#     except Exception as exc:
#         raise HTTPException(status_code=500, detail=f"Load model error: {str(exc)}")


# async def get_model_status():
#     try:
#         async with httpx.AsyncClient() as client:
#             response = await client.get(f"{BEHAVIOURAL_SERVICE_URL}/model_status")
#             response.raise_for_status()
#             return response.json()
#     except httpx.HTTPStatusError as exc:
#         raise HTTPException(status_code=exc.response.status_code, detail=str(exc))
#     except Exception as exc:
#         raise HTTPException(status_code=500, detail=f"Model status fetch error: {str(exc)}")








