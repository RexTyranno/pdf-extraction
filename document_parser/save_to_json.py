from document_parser.models import Document


import json


def save_to_json(document: Document, output_file: str):
    """Saves the Document model to a JSON file."""
    with open(output_file, "w") as f:
        json.dump(document.model_dump(), f, indent=4)