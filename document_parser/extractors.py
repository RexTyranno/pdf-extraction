import fitz  # PyMuPDF
import base64
from typing import List, Optional
from document_parser.models import Image, Table

def filter_footer(lines: List[str]) -> List[str]:
    # Filtering out footer lines and trailing page number from the list of lines
    filtered_lines = [line for line in lines if not line.startswith("Page") and not line.startswith("©")]
    return filtered_lines

def extract_text_from_page(page) -> str:
    # Extracting clean text from a page, excluding footer data and trailing page number
    text = page.get_text("text")
    lines = text.split("\n")
    filtered_lines = filter_footer(lines)
    clean_text = "\n".join(filtered_lines).strip()
    return clean_text

def extract_title_from_text(text: str) -> Optional[str]:
    # Assuming that the title is the first line of the text
    lines = text.split("\n")
    if lines:
        return lines[0].strip()
    return None

def extract_tables_from_page(page) -> List[Table]:
    # Using PyMuPDF's table detection method to extract tables
    tables = []
    detected_tables = page.find_tables()

    previous_table_name = None
    previous_table_obj = None

    for table_index, table in enumerate(detected_tables.tables):
        # Extracting the table content
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
            if columns != previous_table_obj.columns:
                previous_table_obj.rows.append(columns)
            previous_table_obj.rows.extend(rows)
        else:
            table_obj = Table(table_name=table_name, columns=columns, rows=rows)
            tables.append(table_obj)
            previous_table_name = table_name
            previous_table_obj = table_obj
    
    return tables

def extract_images_from_page(page) -> List[Image]:
    # Extracting images from a page and returning them as Image objects with base64 encoded PNG
    images_base64 = []
    img_list = page.get_images(full=True)
    
    for img in img_list:
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