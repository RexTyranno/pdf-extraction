from typing import List, Optional
from pydantic import BaseModel


# Defining the models for the data
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