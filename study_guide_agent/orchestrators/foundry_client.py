import os


class FoundryResponsesClient:
    """
    Thin wrapper that exposes run(payload) for FoundryOrchestrator.
    """

    def __init__(self, openai_client: object, model: str) -> None:
        self.openai_client = openai_client
        self.model = model

    def run(self, payload: dict) -> dict:
        response = self.openai_client.responses.create(
            model=self.model,
            input=payload.get("prompt", ""),
        )
        output_text = getattr(response, "output_text", "")
        return {
            "course_results": [],
            "metrics": {"model": self.model, "output_text_length": len(output_text)},
            "raw_text": output_text,
        }


def create_foundry_client_from_env() -> FoundryResponsesClient:
    endpoint = os.getenv("FOUNDRY_ENDPOINT")
    project = os.getenv("FOUNDRY_PROJECT")
    app = os.getenv("FOUNDRY_APP")
    api_version = os.getenv("FOUNDRY_API_VERSION", "2025-11-15-preview")
    model = os.getenv("FOUNDRY_MODEL", "gpt-4.1")

    if not endpoint or not project or not app:
        raise RuntimeError("Missing Foundry env vars")

    from azure.identity import DefaultAzureCredential, get_bearer_token_provider
    from openai import OpenAI

    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(), "https://ai.azure.com/.default"
    )
    base_url = (
        f"{endpoint.rstrip('/')}/api/projects/{project}/applications/{app}/protocols/openai"
    )

    openai_client = OpenAI(
        api_key=token_provider,
        base_url=base_url,
        default_query={"api-version": api_version},
    )
    return FoundryResponsesClient(openai_client=openai_client, model=model)
