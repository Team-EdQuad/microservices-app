import os
import httpx
from fastapi import HTTPException, UploadFile
from fastapi.responses import StreamingResponse
import io

# ACADEMIC_SERVICE_URL = "http://127.0.0.1:8002"
ACADEMIC_SERVICE_URL = "http://academic:8000"


async def get_content_file_by_id(content_id: str):
    try:
        async with httpx.AsyncClient() as client:
            url = f"{ACADEMIC_SERVICE_URL}/content/file/{content_id}"
            print(f"Calling URL: {url}")
            response = await client.get(url)
            print(f"Response status: {response.status_code}")
            response.raise_for_status()

            content_type = response.headers.get("content-type", "application/octet-stream")
            content_disposition = response.headers.get("content-disposition", "attachment")
            filename = response.headers.get("filename", f"file-{content_id}")
            #Use io.BytesIO for proper StreamingResponse
            return StreamingResponse(
                io.BytesIO(response.content),
                media_type=content_type,
                headers={"Content-Disposition": content_disposition}
            )

    except httpx.HTTPStatusError as exc:
        print(f"[ERROR] HTTPStatusError: {exc.response.status_code} - {exc.response.text}")
        raise HTTPException(status_code=exc.response.status_code, detail=f"HTTP error: {exc.response.text}")
    except Exception as exc:
        print(f"[ERROR] Exception: {str(exc)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(exc)}")
     
async def get_student_list_by_class_and_subject(class_id, subject_id):
    try:
        async with httpx.AsyncClient() as client:
            url = f"{ACADEMIC_SERVICE_URL}/students/{class_id}/{subject_id}"
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=f"HTTP error: {exc.response.text}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error fetching content: {str(exc)}")



async def get_submission_file_by_id(submission_id):
    try:
        async with httpx.AsyncClient() as client:
            url = f"{ACADEMIC_SERVICE_URL}/submission/file/{submission_id}"
            print(f"Calling URL: {url}")
            response = await client.get(url)
            print(f"Response Status: {response.status_code}, Headers: {response.headers}")
            response.raise_for_status()
            
            # Extract the headers we need to forward
            content_type = response.headers.get("content-type", "application/octet-stream")
            content_disposition = response.headers.get("content-disposition", "attachment")
            filename = response.headers.get("filename", f"file-{submission_id}")
            
            # Return a StreamingResponse instead of raw content
            return StreamingResponse(
                iter([response.content]), 
                media_type=content_type,
                headers={"Content-Disposition": content_disposition}
            )
    except httpx.HTTPStatusError as exc:
        print(f"HTTPStatusError: {exc.response.status_code}, {exc.response.text}")
        raise HTTPException(status_code=exc.response.status_code, detail=f"HTTP error: {exc.response.text}")
    except Exception as exc:
        print(f"Exception: {str(exc)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(exc)}")
    

async def get_assignment_file_by_id(assignment_id: str):
    try:
        async with httpx.AsyncClient() as client:
            url = f"{ACADEMIC_SERVICE_URL}/assignment/file/{assignment_id}"
            print(f"Calling URL: {url}")
            response = await client.get(url)
            print(f"Response Status: {response.status_code}, Headers: {response.headers}")
            response.raise_for_status()
            
            # Extract the headers we need to forward
            content_type = response.headers.get("content-type", "application/octet-stream")
            content_disposition = response.headers.get("content-disposition", "attachment")
            filename = response.headers.get("filename", f"file-{assignment_id}")
            
            # Return a StreamingResponse instead of raw content
            return StreamingResponse(
                iter([response.content]), 
                media_type=content_type,
                headers={"Content-Disposition": content_disposition}
            )
    except httpx.HTTPStatusError as exc:
        print(f"HTTPStatusError: {exc.response.status_code}, {exc.response.text}")
        raise HTTPException(status_code=exc.response.status_code, detail=f"HTTP error: {exc.response.text}")
    except Exception as exc:
        print(f"Exception: {str(exc)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(exc)}")
    
    
async def get_subject_names(student_id: str):
    """
    Fetch the list of subjects for a given student by calling the academic service.
    """
    try:
        async with httpx.AsyncClient() as client:
            url = f"{ACADEMIC_SERVICE_URL}/students/{student_id}/subjects"
            response = await client.get(url)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.json()  # Return the JSON response
    except httpx.HTTPStatusError as exc:
        # Handle HTTP errors (e.g., 404, 500)
        raise HTTPException(status_code=exc.response.status_code, detail=f"HTTP error: {exc.response.text}")
    except Exception as exc:
        # Handle other exceptions (e.g., network issues)
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(exc)}")
    
    
async def get_student_content(student_id: str, subject_id: str):
    try:
        async with httpx.AsyncClient() as client:
            url = f"{ACADEMIC_SERVICE_URL}/content/{student_id}/{subject_id}"
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=f"HTTP error: {exc.response.text}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error fetching content: {str(exc)}")

async def get_all_assignments(student_id: str, subject_id: str):
    try:
        async with httpx.AsyncClient() as client:
            url = f"{ACADEMIC_SERVICE_URL}/show_assignments/{student_id}/{subject_id}"
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=f"HTTP error: {exc.response.text}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error fetching assignments: {str(exc)}")
    
async def get_assignment_by_id(assignment_id: str):
    try:
        async with httpx.AsyncClient() as client:
            url = f"{ACADEMIC_SERVICE_URL}/assignment/{assignment_id}"
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=f"HTTP error: {exc.response.text}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error fetching assignment: {str(exc)}")


async def get_assignment_marks(student_id: str):
    try:
        async with httpx.AsyncClient() as client:
            url = f"{ACADEMIC_SERVICE_URL}/submissionmarks/{student_id}"
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=f"HTTP error: {exc.response.text}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error fetching assignment marks: {str(exc)}")


async def get_exam_marks(student_id: str):
    try:
        print(f"Fetching exam marks for student: {student_id}")
        print(f"ACADEMIC_SERVICE_URL: {ACADEMIC_SERVICE_URL}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            url = f"{ACADEMIC_SERVICE_URL}/exammarks/{student_id}"
            print(f"Full request URL: {url}")
            
            response = await client.get(url)
            print(f"Response status: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            
            response.raise_for_status()
            data = response.json()
            print(f"Successfully retrieved {len(data)} exam records")
            return data
            
    except httpx.HTTPStatusError as exc:
        print(f"HTTP Status Error: {exc.response.status_code}")
        print(f"Error response: {exc.response.text}")
        raise HTTPException(status_code=exc.response.status_code, detail=f"HTTP error: {exc.response.text}")
    except httpx.ConnectError as exc:
        print(f"Connection Error: {str(exc)}")
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(exc)}")
    except httpx.TimeoutException as exc:
        print(f"Timeout Error: {str(exc)}")
        raise HTTPException(status_code=504, detail=f"Request timeout: {str(exc)}")
    except Exception as exc:
        print(f"Unexpected error: {type(exc).__name__}: {str(exc)}")
        raise HTTPException(status_code=500, detail=f"Error fetching exam marks: {str(exc)}")


async def upload_assignment_file(student_id: str, assignment_id: str, file: UploadFile):
    try:
        print(f"Starting upload for {student_id}/{assignment_id}")
        async with httpx.AsyncClient(timeout=30.0) as client:
            files = {"file": (file.filename, await file.read(), file.content_type)}
            url = f"{ACADEMIC_SERVICE_URL}/submission/{student_id}/{assignment_id}"
            
            print(f"Sending request to: {url}")
            response = await client.post(url, files=files)
            
            print(f"Response status: {response.status_code}")
            print(f"Response headers: {response.headers}")
            
            response.raise_for_status()
            
            response_data = response.json()
            print(f"Response data received successfully")
            return response_data
            
    except httpx.HTTPStatusError as exc:
        print(f"HTTP Status Error: {exc.response.status_code}")
        print(f"Response text: {exc.response.text}")
        raise HTTPException(status_code=exc.response.status_code, detail=f"HTTP error: {exc.response.text}")
    except httpx.TimeoutException:
        print("Request timeout occurred")
        raise HTTPException(status_code=504, detail="Request timeout")
    except Exception as exc:
        print(f"Unexpected error: {type(exc).__name__}: {str(exc)}")
        raise HTTPException(status_code=500, detail=f"Submission failed: {str(exc)}")

async def mark_content_done(content_id: str, student_id: str): # Now accepts student_id
    try:
        async with httpx.AsyncClient() as client:
            # The URL for the academic service endpoint
            url = f"{ACADEMIC_SERVICE_URL}/content/{content_id}"
            
            # The JSON payload to send
            json_payload = {"student_id": student_id}
            
            # --- THIS IS THE KEY CHANGE ---
            # Add the `json` parameter to your post request
            response = await client.post(url, json=json_payload)
            
            response.raise_for_status() # This will raise an error for 4xx or 5xx responses
            return response.json()
            
    except httpx.HTTPStatusError as exc:
        # Re-raise the error from the downstream service with its details
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.json())
    except httpx.RequestError as exc:
        # Handle connection errors to the academic service
        raise HTTPException(status_code=503, detail=f"Service unavailable: {exc}")
    except Exception as exc:
        # Catch any other unexpected errors
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(exc)}")


###teacher 
async def get_subject_and_class_for_teacher(teacher_id: str):
    try:
        async with httpx.AsyncClient() as client:
            url = f"{ACADEMIC_SERVICE_URL}/subjectNclass/{teacher_id}"
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=f"HTTP error: {exc.response.text}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error fetching subject/class: {str(exc)}")

async def create_assignment_request(class_id: str, subject_id: str, teacher_id: str, form_data: dict, file: UploadFile):
    try:
        async with httpx.AsyncClient() as client:
            url = f"{ACADEMIC_SERVICE_URL}/assignmentcreate/{class_id}/{subject_id}/{teacher_id}"
            data = {
                "assignment_name": form_data["assignment_name"],
                "description": form_data["description"],
                "deadline": form_data["deadline"],
                "grading_type": form_data["grading_type"],
            }
            if form_data["grading_type"] == "auto":
                data["sample_answer"] = form_data.get("sample_answer", "")

            files = {"file": (file.filename, await file.read(), file.content_type)}

            response = await client.post(url, data=data, files=files)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        # Show the backend error for debugging
        print("Backend error:", exc.response.text)
        raise HTTPException(status_code=exc.response.status_code, detail=f"HTTP error: {exc.response.text}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(exc)}")


async def upload_content_request(class_id: str, subject_id: str, content_name: str, description: str, file: UploadFile):
    try:
        async with httpx.AsyncClient() as client:
            url = f"{ACADEMIC_SERVICE_URL}/contentupload/{class_id}/{subject_id}"
            data = {
                "content_name": content_name,
                "description": description,
            }
            files = {"file": (file.filename, await file.read(), file.content_type)}
            response = await client.post(url, data=data, files=files)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=f"HTTP error: {exc.response.text}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error uploading content: {str(exc)}")

async def view_ungraded_manual_submissions(teacher_id: str):
    try:
        async with httpx.AsyncClient() as client:
            url = f"{ACADEMIC_SERVICE_URL}/submission_view/{teacher_id}"
            response = await client.get(url)
            response.raise_for_status()
            return response.json()  # Already returns dict with two keys
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=f"HTTP error: {exc.response.text}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error viewing manual submissions: {str(exc)}")


async def update_manual_marks(teacher_id: str, submission_id: str, marks: float):
    try:
        async with httpx.AsyncClient() as client:
            url = f"{ACADEMIC_SERVICE_URL}/update_submission_marks/{teacher_id}"
            data = {"submission_id": submission_id, "marks": marks}
            response = await client.post(url, data=data)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=f"HTTP error: {exc.response.text}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error updating marks: {str(exc)}")


async def add_exam_marks_request(form_data: dict):
    try:
        async with httpx.AsyncClient() as client:
            url = f"{ACADEMIC_SERVICE_URL}/update_exam_marks"
            response = await client.post(url, data=form_data)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=f"HTTP error: {exc.response.text}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error adding exam marks: {str(exc)}")


async def view_auto_graded_submissions_request(teacher_id: str):
    try:
        async with httpx.AsyncClient() as client:
            url = f"{ACADEMIC_SERVICE_URL}/auto_graded_submissions/{teacher_id}"
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=f"HTTP error: {exc.response.text}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error fetching auto-graded submissions: {str(exc)}")


async def review_auto_graded_marks_request(teacher_id: str, submission_id: str, marks: float, action: str):
    try:
        async with httpx.AsyncClient() as client:
            url = f"{ACADEMIC_SERVICE_URL}/review_auto_graded_marks/{teacher_id}"
            data = {
                "submission_id": submission_id,
                "marks": marks,
                "action": action
            }
            response = await client.post(url, data=data)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=f"HTTP error: {exc.response.text}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error reviewing auto-graded marks: {str(exc)}")
