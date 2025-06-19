import PyPDF2
import os
import io
from typing import Union

def extract_text_from_pdf_path(pdf_file: str) -> str:
    """Extract text from PDF file path"""
    text = ""
    with open(pdf_file, "rb") as pdf:
        reader = PyPDF2.PdfReader(pdf)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text.strip()

def extract_text_from_pdf_bytesio(pdf_bytesio: io.BytesIO) -> str:
    """Extract text from PDF BytesIO object"""
    text = ""
    pdf_bytesio.seek(0)  # Reset pointer to beginning
    reader = PyPDF2.PdfReader(pdf_bytesio)
    for page in reader.pages:
        text += page.extract_text() or ""
    return text.strip()

def extract_text_from_txt_path(txt_file: str) -> str:
    """Extract text from TXT file path"""
    with open(txt_file, "r", encoding="utf-8") as file:
        return file.read().strip()

def extract_text_from_txt_bytesio(txt_bytesio: io.BytesIO) -> str:
    """Extract text from TXT BytesIO object"""
    txt_bytesio.seek(0)  # Reset pointer to beginning
    content = txt_bytesio.read().decode('utf-8')
    return content.strip()

def extract_text(file_input: Union[str, io.BytesIO], filename: str = None) -> str:
    """
    Extract text from file input (file path string or BytesIO object)
    
    Args:
        file_input: Either a file path string or BytesIO object
        filename: Required when file_input is BytesIO to determine file type
    """
    
    if isinstance(file_input, str):
        # Handle file path
        if file_input.endswith(".pdf"):
            return extract_text_from_pdf_path(file_input)
        elif file_input.endswith(".txt"):
            return extract_text_from_txt_path(file_input)
        else:
            raise ValueError(f"Unsupported file type: {file_input}")
    
    elif isinstance(file_input, io.BytesIO):
        # Handle BytesIO object
        if not filename:
            raise ValueError("Filename is required when using BytesIO object")
        
        if filename.endswith(".pdf"):
            return extract_text_from_pdf_bytesio(file_input)
        elif filename.endswith(".txt"):
            return extract_text_from_txt_bytesio(file_input)
        else:
            raise ValueError(f"Unsupported file type: {filename}")
    
    else:
        raise ValueError(f"Unsupported input type: {type(file_input)}")
