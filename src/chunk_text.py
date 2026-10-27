
import pymupdf
from pathlib import Path

# Locate the project folders
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"

# Chunking settings
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100


def split_into_chunks(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Split text into overlapping character-based chunks."""

    if chunk_size <= 0:
        raise ValueError("Chunk size must be greater than zero.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("Overlap must be non-negative and smaller than chunk size.")

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        # Move forward while retaining some previous text
        start += chunk_size - overlap

    return chunks


# Find the PDF
pdf_files = list(DATA_DIR.glob("*.pdf"))

if not pdf_files:
    print("No PDF found in the data folder.")

else:
    pdf_path = pdf_files[0]

    # Extract text from all pages
    with pymupdf.open(pdf_path) as document:
        full_text = "\n".join(
            page.get_text()
            for page in document
        )

    if not full_text.strip():
        print("No extractable text found in the PDF.")
    else:
        # Split the extracted text into chunks
        chunks = split_into_chunks(full_text)

        print(f"PDF: {pdf_path.name}")
        print(f"Total characters: {len(full_text)}")
        print(f"Total chunks: {len(chunks)}")

        # Display the first three chunks
        for index, chunk in enumerate(chunks[:3], start=1):
            print(f"\n--- Chunk {index} ---")
            print(chunk)
