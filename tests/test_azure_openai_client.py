from unittest.mock import patch

import pytest

from study_guide_agent.orchestrators.azure_openai_client import (
    create_azure_openai_client_from_env,
)


def test_create_client_requires_endpoint(monkeypatch):
    monkeypatch.delenv("AZURE_OPENAI_ENDPOINT", raising=False)
    with pytest.raises(RuntimeError, match="Missing AZURE_OPENAI_ENDPOINT"):
        create_azure_openai_client_from_env()


@patch("study_guide_agent.orchestrators.azure_openai_client.OpenAI")
def test_create_client_uses_api_key_when_set(openai_mock, monkeypatch):
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://x.services.ai.azure.com")
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "secret")
    create_azure_openai_client_from_env()
    openai_mock.assert_called_once()
    call_kw = openai_mock.call_args[1]
    assert call_kw["api_key"] == "secret"
    assert call_kw["base_url"].endswith("/openai/v1/")


@patch("study_guide_agent.orchestrators.azure_openai_client.OpenAI")
@patch("study_guide_agent.orchestrators.azure_openai_client.get_bearer_token_provider")
@patch("study_guide_agent.orchestrators.azure_openai_client.DefaultAzureCredential")
def test_create_client_uses_entra_when_no_key(
    cred_mock, token_provider_mock, openai_mock, monkeypatch
):
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://x.services.ai.azure.com")
    monkeypatch.delenv("AZURE_OPENAI_API_KEY", raising=False)
    token_provider_mock.return_value = "token-provider"
    create_azure_openai_client_from_env()
    openai_mock.assert_called_once()
    call_kw = openai_mock.call_args[1]
    assert call_kw["api_key"] == "token-provider"
    assert call_kw["base_url"].endswith("/openai/v1/")
    token_provider_mock.assert_called_once()
    cred_mock.assert_called_once()
