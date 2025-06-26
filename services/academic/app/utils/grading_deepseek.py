import os
from openai import OpenAI
import re

def grade_answer_deepseek(teacher_answer: str, student_answer: str) -> int:
    """Send answers to DeepSeek AI for grading and extract only the numerical score."""
    

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY not found in environment variables")
    
    # Initialize DeepSeek client (compatible with OpenAI SDK)
    client = OpenAI(
        api_key=api_key,  
        base_url="https://api.deepseek.com"
    )

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
        response = client.chat.completions.create(
            model="deepseek-chat",  # Use deepseek-chat for regular tasks
            messages=[
                {"role": "system", "content": "You are a helpful grading assistant."},
                {"role": "user", "content": prompt}
            ],
            stream=False
        )
        
        # Extract numeric score using regex
        response_text = response.choices[0].message.content
        match = re.search(r"\b\d+\b", response_text)
        if match:
            return int(match.group())
        else:
            raise ValueError("DeepSeek AI did not return a valid grade.")
            
    except Exception as e:
        raise ValueError(f"DeepSeek grading failed: {str(e)}")
