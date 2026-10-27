
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer("all-MiniLM-L6-v2")

sentences = [
    "How can I check CPU usage in Linux?",
    "Which command shows processor utilization?",
    "I enjoy eating pizza."
]

embeddings = model.encode(sentences)

similarity_matrix = cosine_similarity(embeddings)

for i in range(len(sentences)):
    for j in range(i + 1, len(sentences)):
        score = similarity_matrix[i][j]

        print(f"\nSentence A: {sentences[i]}")
        print(f"Sentence B: {sentences[j]}")
        print(f"Cosine similarity: {score:.4f}")
