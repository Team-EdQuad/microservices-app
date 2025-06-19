import httpx
from fastapi import HTTPException
import logging

BEHAVIOURAL_SERVICE_URL = "http://127.0.0.1:8005"



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


async def active_time_prediction(input_data: dict):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{BEHAVIOURAL_SERVICE_URL}/predict_active_time", json=input_data)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(exc)}")



async def model_train():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{BEHAVIOURAL_SERVICE_URL}/train")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Training error: {str(exc)}")


async def load_model():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{BEHAVIOURAL_SERVICE_URL}/load_model")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Load model error: {str(exc)}")


async def get_model_status():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BEHAVIOURAL_SERVICE_URL}/model_status")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Model status fetch error: {str(exc)}")








