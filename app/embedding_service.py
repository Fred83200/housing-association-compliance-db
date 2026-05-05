import os
from openai import OpenAI

_client = None

def _get_client():
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")
        _client = OpenAI(api_key=api_key)
    return _client

def get_embedding(text: str) -> list[float]:
    response = _get_client().embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding