import fitz  # PyMuPDF
import json
from document_parser.extractors import (
    extract_text_from_page,
    extract_title_from_text,
    extract_tables_from_page,
    extract_images_from_page
)
from document_parser.models import Document, Page

def process_pdf(pdf_path: str) -> Document:
    #Fitz is used to open the PDF and extract metadata
    doc = fitz.open(pdf_path)
    
    # Extracting metadata from the PDF
    document_title = doc.metadata.get("title", "Untitled Document")
    author = doc.metadata.get("author", None)
    date = doc.metadata.get("creationDate", None)
    
    # Processing each page of the PDF
    pages = []
    for page_number in range(doc.page_count):
        page = doc.load_page(page_number)
        
        text = extract_text_from_page(page)
        title = extract_title_from_text(text)
        tables = extract_tables_from_page(page)
        images = extract_images_from_page(page)
        
        page_data = Page(
            page_number=page_number + 1,
            text=text,
            title=title,
            tables=tables,
            images=images
        )
        pages.append(page_data)
    
    document = Document(
        document_title=document_title,
        author=author,
        date=date,
        pages=pages
    )
    
    return document

def save_to_json(document: Document, output_file: str):
    """Saves the Document model to a JSON file."""
    with open(output_file, "w") as f:
        json.dump(document.model_dump(), f, indent=4) 