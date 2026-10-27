
import pymupdf
from pathlib import Path

# Locate the project directory
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"

# Find PDF files in the data folder
pdf_files = list(DATA_DIR.glob("*.pdf"))

if not pdf_files:
    print("No PDF found in the data folder.")
else:
    pdf_path = pdf_files[0]

    print(f"Reading PDF: {pdf_path.name}")

    # Open the PDF
    document = pymupdf.open(pdf_path)

    # Extract text from every page
    for page_number, page in enumerate(document, start=1):
        text = page.get_text()

        print(f"\n--- Page {page_number} ---")
        print(text if text.strip() else "[No text found on this page]")

    document.close()
