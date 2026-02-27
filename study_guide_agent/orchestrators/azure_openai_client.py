import os

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import OpenAI


def create_azure_openai_client_from_env() -> OpenAI:
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    if not endpoint:
        raise RuntimeError("Missing AZURE_OPENAI_ENDPOINT")

    base_url = endpoint.rstrip("/")
    if "/openai/v1" not in base_url:
        base_url = f"{base_url}/openai/v1"
    base_url = f"{base_url.rstrip('/')}/"

    if api_key:
        return OpenAI(api_key=api_key, base_url=base_url)

    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
    )
    return OpenAI(api_key=token_provider, base_url=base_url)
