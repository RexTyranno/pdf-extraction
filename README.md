# PDF Document Parser

This project is a command line tool that processes PDF files and converts them into a structured JSON format. It supports two modes of operation:

- **Digital PDF Mode:** Uses PyMuPDF to extract text, tables, and images directly from digitally created PDFs.
- **Scanned PDF Mode:** Uses OCR (via pytesseract) to extract text and images from scanned PDFs.

## Installation

1. **Clone the Repository**

   Clone the repository to your local machine:

   ```bash
   git clone https://github.com/yourusername/pdf-document-parser.git
   cd pdf-document-parser
   ```

2. **Create a Virtual Environment (Optional but Recommended)**

   Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install Dependencies**

   Install the required Python packages using `pip`:

   ```bash
   pip install -r requirements.txt
   ```

4. **Additional Requirements for OCR (Scanned PDF Mode)**

   - **Tesseract-OCR:**  
     Install Tesseract on your system.

     - **Ubuntu:** `sudo apt-get install tesseract-ocr`
     - **macOS (Homebrew):** `brew install tesseract`
     - **Windows:** Download and install from [Tesseract at UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)

   - **Poppler:**  
     `pdf2image` requires Poppler to convert PDF pages to images.
     - **Ubuntu:** `sudo apt-get install poppler-utils`
     - **macOS (Homebrew):** `brew install poppler`
     - **Windows:** Download from [Poppler for Windows](http://blog.alivate.com.au/poppler-windows/), and add the bin folder to your PATH.

## Usage

Run the tool from the command line. The main script (`main.py`) accepts the following arguments:

- `pdf_path`: Path to the input PDF file.
- `output_path`: Path where the JSON output file will be saved.
- `--scanned`: (Optional) Use this flag to process the PDF as a scanned document using OCR.

### Example Commands

- **Process a Digital PDF:**

  ```bash
  python main.py path/to/digital.pdf output.json
  ```

- **Process a Scanned PDF:**
  ```bash
  python main.py path/to/scanned.pdf output.json --scanned
  ```

## How It Works

1. **Command Line Argument Parsing:**

   - The entry point of the application is the `main()` function in `main.py`, which uses the `argparse` module to handle command-line arguments.
   - The `--scanned` flag determines whether the PDF is processed as scanned (using OCR) or as digital.

2. **Digital PDF Processing:**

   - In digital mode, the `process_pdf` function (in `document_parser/pdf_processor.py`) is called.
   - This function leverages PyMuPDF to open the PDF and read metadata (title, author, and date).
   - It iterates through each page of the PDF, extracting:
     - **Text:** Cleaned up by removing footers using functions from `document_parser/extractors.py`.
     - **Title:** Assumed to be the first line of text.
     - **Tables:** Extracted using built-in table detection features from PyMuPDF.
     - **Images:** Extracted and converted to a base64 encoded PNG.
   - The extracted data is structured using Pydantic models defined in `document_parser/models.py`.

3. **Scanned PDF Processing:**

   - In scanned mode, the `process_scanned_pdf` function (in `document_parser/ocr_pdf_processor.py`) is used.
   - It first extracts metadata via PyMuPDF.
   - Then, it converts each page to an image using the `pdf2image` library.
   - The OCR is applied using `pytesseract` to extract text from these images.
   - Images are saved as base64 encoded PNGs.
   - Since table extraction from scanned PDFs is non-trivial with OCR, tables are left empty.

4. **Saving the Output:**
   - The structured Document (with pages, text, images, etc.) is saved as JSON using the helper function in `document_parser/save_to_json.py`.

This clear separation of functionality into modules makes the codebase modular and extensible. Enjoy using the PDF Document Parser, and feel free to contribute or raise issues on the repository!
