import PyPDF2
import os

def extract_text_from_pdf(pdf_file: str) -> str:
    text = ""
    with open(pdf_file, "rb") as pdf:
        reader = PyPDF2.PdfReader(pdf)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text.strip()

def extract_text_from_txt(txt_file: str) -> str:
    with open(txt_file, "r", encoding="utf-8") as file:
        return file.read().strip()

def extract_text(file_path: str) -> str:
    if file_path.endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith(".txt"):
        return extract_text_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_path}")