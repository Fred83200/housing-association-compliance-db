import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

_client = None


def _get_client():
    global _client
    if _client is None:
        if os.getenv("AZURE_KEYVAULT_URI"):
            from app.key_vault import get_secret
            api_key = get_secret("openai-api-key")
        else:
            api_key = os.getenv("AZURE_OPENAI_API_KEY")
        _client = AzureOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=api_key,
            api_version="2024-12-01-preview",
        )
    return _client


def llm_generate_response(messages):
    response = _get_client().chat.completions.create(
        model=os.getenv("AZURE_AI_DEPLOYMENT", "gpt-4o"),
        messages=messages,
    )
    return response.choices[0].message.content
