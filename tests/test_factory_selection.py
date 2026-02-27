import pytest

from study_guide_agent.orchestrators import create_orchestrator
from study_guide_agent.storage import create_storage


def test_create_orchestrator_gemini_strategy():
    orchestrator = create_orchestrator("gemini")
    assert orchestrator.__class__.__name__ == "GeminiOrchestrator"


def test_create_orchestrator_foundry_strategy(monkeypatch):
    class FakeClient:
        def run(self, payload):
            return {"course_results": [], "metrics": {}}

    monkeypatch.setattr(
        "study_guide_agent.orchestrators.create_foundry_client_from_env",
        lambda: FakeClient(),
    )
    orchestrator = create_orchestrator("foundry")
    assert orchestrator.__class__.__name__ == "FoundryOrchestrator"


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
