import os
import voyageai
from dotenv import load_dotenv

load_dotenv()

VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY")
if not VOYAGE_API_KEY:
    raise ValueError("VOYAGE_API_KEY is not set in .env")

vo = voyageai.Client(api_key=VOYAGE_API_KEY)


def generate_embedding(text: str) -> list[float]:
    result = vo.embed([text], model="voyage-3", input_type="document")
    return result.embeddings[0]
