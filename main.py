import fitz  # PyMuPDF
import base64
import io
import json
from typing import List, Dict, Optional
from pydantic import BaseModel, Field

# Pydantic models to structure the data
class Image(BaseModel):
    image_base64: str

class Table(BaseModel):
    table_name: str
    columns: List[str]
    rows: List[List]

class Page(BaseModel):
    page_number: int
    text: str
    title: Optional[str] = None
    tables: List[Table] = []
    images: List[Image] = []
    
class Document(BaseModel):
    document_title: str
    author: Optional[str] = None
    date: Optional[str] = None
    pages: List[Page]


def filter_footer(lines: List[str]) -> List[str]:
    """Filters out footer lines and trailing page number from the list of lines."""
    filtered_lines = [line for line in lines if not line.startswith("Page") and not line.startswith("©")]
    return filtered_lines

def extract_text_from_page(page) -> str:
    """Extracts clean text from a page, excluding footer data and trailing page number."""
    text = page.get_text("text")
    lines = text.split("\n")
    filtered_lines = filter_footer(lines)
    clean_text = "\n".join(filtered_lines).strip()
    return clean_text

def extract_title_from_text(text: str) -> Optional[str]:
    """Simple method to extract title, assuming the title is at the start of the text."""
    lines = text.split("\n")
    if lines:
        return lines[0].strip()
    return None

def extract_tables_from_page(page) -> List[Table]:
    """Extract tables from a page using PyMuPDF's table detection."""
    tables = []
    # detect tables using PyMuPDF's find_tables method
    detected_tables = page.find_tables()

    previous_table_name = None
    previous_table_obj = None

    for table_index, table in enumerate(detected_tables.tables):
        # Extract the table content
        table_content = table.extract()
        
        # Assuming the first row is the header
        columns = table_content[0] if table_content else []
        rows = table_content[1:] if len(table_content) > 1 else []
        
        # Attempt to find the table name by checking text blocks after the table
        table_name = f"Extracted Table {table_index + 1}"
        text_blocks = page.get_text("blocks")
        
        # Access the bounding rectangle of the table
        table_rect = table.bbox  # Use the correct attribute or method to get the bounding box
        
        # Finding text blocks below the table for table name
        for block in text_blocks:
            block_rect = fitz.Rect(block[:4])
            if block_rect.y0 > table_rect[3]:  # Checking if the block is below the table
                potential_name = block[4].strip()
                if potential_name.startswith("Table") or potential_name.startswith("Figure"):
                    table_name = potential_name
                    break
        
        # Checking if the table has been extracted before or was fragmented
        if previous_table_name and previous_table_name == table_name:
            # Checking if the first row of the current table is the same as the columns of the previous table
            if columns != previous_table_obj.columns:
                # If different, treating the first row as a new set of columns
                previous_table_obj.rows.append(columns)
            # Merging the current table with the previous one
            previous_table_obj.rows.extend(rows)
        else:
            # Creating a new Table object
            table_obj = Table(table_name=table_name, columns=columns, rows=rows)
            tables.append(table_obj)
            previous_table_name = table_name
            previous_table_obj = table_obj
    
    return tables

def extract_images_from_page(page) -> List[str]:
    # Extracting images from a page and returning them as base64 strings for better memory management and json storage
    images_base64 = []
    img_list = page.get_images(full=True)
    
    for img_index, img in enumerate(img_list):
        xref = img[0]
        base_image = fitz.Pixmap(page.parent, xref)
        
        # Convert to RGB if the image is not already grayscale or RGB
        if base_image.colorspace.name not in ["DeviceGray", "DeviceRGB"]:
            base_image = fitz.Pixmap(fitz.csRGB, base_image)
        
        img_bytes = base_image.tobytes("png")
        img_base64 = base64.b64encode(img_bytes).decode("utf-8")
        images_base64.append(Image(image_base64=img_base64))
        
        base_image = None  # Free memory
    
    return images_base64

def process_pdf(pdf_path: str) -> Document:
    # Main function to process the PDF and extract data
    doc = fitz.open(pdf_path)
    
    # Extracting document title and author from metadata
    document_title = doc.metadata.get("title", "Untitled Document")
    author = doc.metadata.get("author", None)
    date = doc.metadata.get("creationDate", None)
    
    pages = []
    for page_number in range(doc.page_count):
        page = doc.load_page(page_number)
        
        # Extracting text, tables, and images from the page
        text = extract_text_from_page(page)
        title = extract_title_from_text(text)
        tables = extract_tables_from_page(page)
        images_base64 = extract_images_from_page(page)
        
        page_data = Page(
            page_number=page_number + 1,
            text=text,
            title=title,
            tables=tables,
            images=images_base64
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
    # Saving the document to a JSON file
    with open(output_file, "w") as f:
        json.dump(document.model_dump(), f, indent=4)


pdf_path = "ConceptsofBiology-WEB-1-68.pdf"  # PDF file path
output_json_path = "output.json"  # Output JSON file path

document = process_pdf(pdf_path)
save_to_json(document, output_json_path)
print(f"PDF data saved to {output_json_path}")

