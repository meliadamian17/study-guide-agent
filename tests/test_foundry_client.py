import pytest

from study_guide_agent.orchestrators.foundry_client import (
    FoundryResponsesClient,
    create_foundry_client_from_env,
)


class _FakeResponses:
    def __init__(self):
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)

        class _Resp:
            output_text = "ok"

        return _Resp()


class _FakeOpenAIClient:
    def __init__(self):
        self.responses = _FakeResponses()


def test_foundry_responses_client_run_maps_payload():
    fake = _FakeOpenAIClient()
    client = FoundryResponsesClient(openai_client=fake, model="gpt-4.1")

    result = client.run({"prompt": "sync now"})

    assert fake.responses.calls[0]["model"] == "gpt-4.1"
    assert fake.responses.calls[0]["input"] == "sync now"
    assert result["metrics"]["output_text_length"] == 2


def test_create_foundry_client_from_env_missing_required_vars(monkeypatch):
    monkeypatch.delenv("FOUNDRY_ENDPOINT", raising=False)
    monkeypatch.delenv("FOUNDRY_PROJECT", raising=False)
    monkeypatch.delenv("FOUNDRY_APP", raising=False)

    with pytest.raises(RuntimeError, match="Missing Foundry env vars"):
        create_foundry_client_from_env()
