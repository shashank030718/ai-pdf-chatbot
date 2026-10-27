
import pymupdf
import faiss
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 100
TOP_K = 3


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


# Extract text from a readable PDF
full_text = ""

for pdf_path in DATA_DIR.glob("*.pdf"):
    with pymupdf.open(pdf_path) as document:
        text = "\n".join(page.get_text() for page in document)

    if text.strip():
        print("Using PDF:", pdf_path.name)
        full_text = text
        break

if not full_text.strip():
    raise ValueError("No extractable text found in the PDF folder.")

chunks = split_into_chunks(full_text)

# Create embeddings for all chunks
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(
    chunks,
    convert_to_numpy=True
)

# Build the FAISS index
embeddings = np.asarray(embeddings, dtype="float32")
faiss.normalize_L2(embeddings)

index = faiss.IndexFlatIP(embeddings.shape[1])
index.add(embeddings)

print("\nChunks indexed:", index.ntotal)

# Ask a question about the PDF
question = input("\nAsk a question about your PDF: ")

question_embedding = model.encode(
    [question],
    convert_to_numpy=True
).astype("float32")

faiss.normalize_L2(question_embedding)

# Retrieve the top 3 most similar chunks
scores, indices = index.search(question_embedding, TOP_K)

print("\nMost relevant PDF chunks:")

for rank, (score, chunk_index) in enumerate(
    zip(scores[0], indices[0]), start=1
):
    print(f"\n--- Result {rank} | Similarity: {score:.4f} ---")
    print(chunks[chunk_index])
