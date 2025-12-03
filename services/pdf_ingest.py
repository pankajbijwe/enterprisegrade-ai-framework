# pdf_ingest.py - PDF extraction utilities 
# services/pdf_ingest.py
from pypdf import PdfReader
from typing import List
import io

def extract_text_from_pdf(content: bytes) -> str:
    """
    Extract text from PDF bytes. For scanned PDFs, integrate OCR (Tesseract) in production.
    """
    reader = PdfReader(io.BytesIO(content))
    pages = []
    for p in reader.pages:
        pages.append(p.extract_text() or "")
    return "\n".join(pages)