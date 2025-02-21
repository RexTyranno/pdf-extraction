from document_parser.pdf_processor import process_pdf, save_to_json

if __name__ == "__main__":
    pdf_path = "ConceptsofBiology-WEB-1-68.pdf"  # PDF file path
    output_json_path = "output.json"             # Output JSON file path

    document = process_pdf(pdf_path)
    save_to_json(document, output_json_path)
    print(f"PDF data saved to {output_json_path}")

