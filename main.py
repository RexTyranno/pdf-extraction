import argparse # For parsing command line arguments
from document_parser.pdf_processor import process_pdf, save_to_json as save_to_json_digital
from document_parser.ocr_pdf_processor import process_scanned_pdf, save_to_json as save_to_json_scanned

def main():
    parser = argparse.ArgumentParser(description="Process a PDF file as digital or scanned.")
    parser.add_argument("pdf_path", type=str, help="Path to the PDF file.") 
    parser.add_argument("output_path", type=str, help="Path for the JSON output file.")  
    parser.add_argument("--scanned", action="store_true", help="Process the PDF as scanned (using OCR).") # --scanned argument to process the PDF as scanned
    args = parser.parse_args()

    if args.scanned:
        print("Processing PDF as scanned using OCR...")
        document = process_scanned_pdf(args.pdf_path)
        save_to_json_scanned(document, args.output_path)
    else:
        print("Processing PDF as digital...")
        document = process_pdf(args.pdf_path)
        save_to_json_digital(document, args.output_path)

    print(f"PDF data saved to {args.output_path}")

if __name__ == "__main__":
    main()

