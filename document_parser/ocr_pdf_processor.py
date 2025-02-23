import fitz  # Only used for metadata extraction
import pytesseract
from pdf2image import convert_from_path
import base64
from io import BytesIO
import json

from document_parser.models import Document, Page, Image as ImageModel
from document_parser.extractors import extract_title_from_text

def process_scanned_pdf(pdf_path: str) -> Document:
    
    # Using fitz to open the PDF and extract metadata
    doc = fitz.open(pdf_path)
    document_title = doc.metadata.get("title", "Untitled Document")
    author = doc.metadata.get("author", None)
    date = doc.metadata.get("creationDate", None)
    
    # Convert PDF pages to images for OCR (dpi for better quality)
    pil_images = convert_from_path(pdf_path, dpi=300)
    
    pages = []
    for i, pil_image in enumerate(pil_images):
        # Extract text from the image using pytesseract OCR
        text = pytesseract.image_to_string(pil_image)
        title = extract_title_from_text(text)
        
        #returning empty tables as OCR-based table extraction is non-trivial
        page_data = Page(
            page_number=i + 1,
            text=text,
            title=title,
            tables=[],          # OCR-based table extraction not implemented
            images=[]
        )
        pages.append(page_data)
    
    document = Document(
        document_title=document_title,
        author=author,
        date=date,
        pages=pages
    )
    return document