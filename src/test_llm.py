
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY not found. Check your project-root .env file."
    )

client = genai.Client(api_key=api_key)

interaction = client.interactions.create(
    model="gemini-3.5-flash-lite",
    input="Explain RAG in two simple sentences."
)

print(interaction.output_text)
