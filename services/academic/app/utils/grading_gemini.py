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
    print("GEMINI_API_KEY in grading_gemini.py:", os.getenv("GEMINI_API_KEY"))
    # Configure Gemini with your API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    
    genai.configure(api_key=api_key)
    
    # Use the free Gemini 2.0 Flash model (best free option)
    model = genai.GenerativeModel("models/gemini-2.0-flash-exp")

    prompt = f"""
    You are a fair and intelligent grading assistant. Your task is to grade a student's answer using the teacher's sample answer as a **reference**, not as the only correct version.

    Use the following criteria:
    1. **Correctness (40%)** – Is the student's answer factually correct, even if phrased differently?
    2. **Completeness (30%)** – Does the student cover the important points addressed in the teacher's sample or that are clearly relevant to the question?
    3. **Relevance (20%)** – Does the student stay on-topic and address the actual question?
    4. **Clarity (10%)** – Is the answer well-structured and understandable?

    Guidelines:
    - Use the teacher's answer as guidance, but be open to alternative valid responses.
    - Be unbiased. Don't penalize for different wording or extra correct points.
    - Only return a final **numeric score between 0 and 100**. Do not explain or write any text.

    Teacher's Sample Answer:
    {teacher_answer}

    Student's Answer:
    {student_answer}

    Final Score:
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
