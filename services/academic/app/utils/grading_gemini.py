import google.generativeai as genai
import re
import os
import time
from datetime import datetime, timedelta

class GeminiRateLimiter:
    def __init__(self):
        self.last_request = None
        self.min_interval = 4  # 4 seconds between requests (15 RPM = 4 sec interval)
    
    def wait_if_needed(self):
        if self.last_request:
            elapsed = datetime.now() - self.last_request
            if elapsed < timedelta(seconds=self.min_interval):
                wait_time = self.min_interval - elapsed.total_seconds()
                time.sleep(wait_time)
        self.last_request = datetime.now()

# Use in your grading function
rate_limiter = GeminiRateLimiter()

def grade_answer(teacher_answer: str, student_answer: str) -> int:
    """Send answers to Gemini Free for grading and extract only the numerical score."""
    
    # Configure Gemini with your API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    
    genai.configure(api_key=api_key)
    
    # Use the free Gemini 2.0 Flash model (best free option)
    model = genai.GenerativeModel("models/gemini-2.0-flash-exp")

    prompt = f"""
    You are an AI grading assistant. Compare the student's answer with the teacher's sample answer.
    - Assign a grade between **0 to 100** based on correctness, completeness, and relevance.
    - Only return a number. No extra text.

    **Teacher's Sample Answer:**  
    {teacher_answer}

    **Student's Answer:**  
    {student_answer}

    **Output Format:**  
    - (score between 0-100)
    """

    try:
        response = model.generate_content(prompt)
        
        # Extract numeric score using regex
        match = re.search(r"\b\d+\b", response.text)
        if match:
            return int(match.group())
        else:
            raise ValueError("Gemini did not return a valid grade.")
            
    except Exception as e:
        raise ValueError(f"Gemini grading failed: {str(e)}")
