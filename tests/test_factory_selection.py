import pytest

from study_guide_agent.orchestrators import create_orchestrator
from study_guide_agent.storage import create_storage


def test_create_orchestrator_azure_openai_strategy(monkeypatch):
    monkeypatch.setenv("AZURE_OPENAI_MODEL", "kimi-k2.5")
    monkeypatch.setenv("STORAGE_PROVIDER", "azure")
    monkeypatch.setenv("CANVAS_TOKEN", "token")

    class FakeClient:
        pass

    monkeypatch.setattr(
        "study_guide_agent.orchestrators.create_azure_openai_client_from_env",
        lambda: FakeClient(),
    )

    orchestrator = create_orchestrator("azure_openai")
    assert orchestrator.__class__.__name__ == "AzureOpenAIOrchestrator"
    assert orchestrator.model == "kimi-k2.5"


def test_create_orchestrator_azure_openai_missing_model_raises(monkeypatch):
    monkeypatch.delenv("AZURE_OPENAI_MODEL", raising=False)
    with pytest.raises(RuntimeError, match="Missing AZURE_OPENAI_MODEL"):
        create_orchestrator("azure_openai")


def test_create_orchestrator_unknown_provider_raises():
    with pytest.raises(ValueError, match="Unknown agent provider"):
        create_orchestrator("nope")


def test_create_storage_gcs_strategy():
    storage = create_storage("gcs")
    assert storage.__class__.__name__ == "GCSStorage"


def test_create_storage_azure_strategy():
    storage = create_storage("azure")
    assert storage.__class__.__name__ == "AzureBlobStorage"


def test_create_storage_unknown_provider_raises():
    with pytest.raises(ValueError, match="Unknown storage provider"):
        create_storage("nope")
