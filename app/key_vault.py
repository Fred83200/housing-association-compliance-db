import os
from functools import lru_cache

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient


@lru_cache(maxsize=None)
def _client() -> SecretClient:
    vault_uri = os.getenv("AZURE_KEYVAULT_URI")
    if not vault_uri:
        raise RuntimeError("AZURE_KEYVAULT_URI is not set")
    return SecretClient(vault_url=vault_uri, credential=DefaultAzureCredential())


def get_secret(name: str) -> str:
    return _client().get_secret(name).value
