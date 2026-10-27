
import pymupdf
from pathlib import Path
from sentence_transformers import SentenceTransformer

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 100


def split_into_chunks(text):
    chunks = []
    start = 0

    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks


# Find a PDF containing extractable text
pdf_files = list(DATA_DIR.glob("*.pdf"))

if not pdf_files:
    raise FileNotFoundError("Place a PDF inside the data folder.")

full_text = ""

for pdf_path in pdf_files:
    with pymupdf.open(pdf_path) as document:
        text = "\n".join(page.get_text() for page in document)

    if text.strip():
        print(f"Using PDF: {pdf_path.name}")
        full_text = text
        break

if not full_text.strip():
    raise ValueError("No extractable PDF text found.")

chunks = split_into_chunks(full_text)

print("Total chunks:", len(chunks))

# Load our embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Convert each chunk into a vector
embeddings = model.encode(
    chunks,
    convert_to_numpy=True,
    show_progress_bar=True
)

print("Embedding shape:", embeddings.shape)
print("First chunk:\n", chunks[0])
print("First vector dimensions:", len(embeddings[0]))
