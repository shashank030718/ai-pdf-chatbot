
from sentence_transformers import SentenceTransformer

# Load a pretrained embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Two sentences with similar meanings
sentences = [
    "How can I check CPU usage in Linux?",
    "Which command shows processor utilization?",
    "I enjoy eating pizza."
]

# Convert sentences into numerical vectors
embeddings = model.encode(sentences)

# Display the results
print("Number of sentences:", len(sentences))
print("Embedding shape:", embeddings.shape)

print("\nFirst sentence embedding (first 10 numbers):")
print(embeddings[0][:10])

print("\nSecond sentence embedding (first 10 numbers):")
print(embeddings[1][:10])
