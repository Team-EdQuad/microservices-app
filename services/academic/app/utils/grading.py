
import re
import google.generativeai as genai

from .file_utils import extract_text

def grade_answer(teacher_answer: str, student_answer: str) -> int:
    """Send answers to Gemini AI for grading and extract only the numerical score."""
    model = genai.GenerativeModel("models/gemini-1.5-pro-latest")

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

    response = model.generate_content(prompt)

    # Extract numeric score using regex
    match = re.search(r"\b\d+\b", response.text)
    if match:
        return int(match.group())  # Convert extracted number to int
    else:
        raise ValueError("Gemini AI did not return a valid grade.")

def test_grading(teacher_file, student_file):
    """Manually test AI grading with a sample teacher and student answer."""
    from utils.file_utils import extract_text
    
    teacher_text = extract_text(teacher_file)
    student_text = extract_text(student_file)

    grade = grade_answer(teacher_text, student_text)
    print(f" AI-Generated Grade: {grade}")
    return grade



# Testing Function 
def test_grading():
    """Manually test AI grading with a sample teacher and student answer."""
    teacher_text = extract_text("sample_teacher_answer.pdf")  # Change to actual file
    student_text = extract_text("student_submission.pdf")  # Change to actual file

    grade = grade_answer(teacher_text, student_text)
    print(f"AI-Generated Grade: {grade}")

