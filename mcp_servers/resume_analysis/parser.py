import fitz  # PyMuPDF
import pdfplumber

def extract_text_pymupdf(pdf_path: str) -> str:
    text = ""
    doc = fitz.open(pdf_path)
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

def extract_text_pdfplumber(pdf_path: str) -> str:
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def extract_resume_text(pdf_path: str) -> str:
    """Try PyMuPDF first (faster), fall back to pdfplumber (better for complex layouts)."""
    text = extract_text_pymupdf(pdf_path)
    if len(text.strip()) < 50:
        text = extract_text_pdfplumber(pdf_path)
    return text