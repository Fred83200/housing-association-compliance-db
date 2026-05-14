import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = AzureOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2024-12-01-preview",
        )
    return _client


def get_embedding(text: str) -> list[float]:
    response = _get_client().embeddings.create(
        model=os.getenv("AZURE_EMBEDDING_DEPLOYMENT", "text-embedding-3-small"),
        input=text,
    )
    return response.data[0].embedding
