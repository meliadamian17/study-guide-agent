import pytest

from study_guide_agent.models import StudyGuideConfig
from study_guide_agent.orchestrators.foundry import FoundryOrchestrator


class FakeFoundryClient:
    def __init__(self, response: dict):
        self.response = response
        self.calls = []

    def run(self, payload: dict) -> dict:
        self.calls.append(payload)
        return self.response


def test_foundry_orchestrator_calls_client_with_expected_payload():
    client = FakeFoundryClient(
        {"course_results": [{"course_id": "7", "status": "updated"}], "metrics": {"latency_ms": 5}}
    )
    orchestrator = FoundryOrchestrator(client=client, mcp_endpoint="https://mcp.example")
    config = StudyGuideConfig(agent_provider="foundry", storage_provider="azure", task_prompt="sync")

    outcome = orchestrator.invoke("sync", config)

    assert client.calls[0]["prompt"] == "sync"
    assert client.calls[0]["mcp_endpoint"] == "https://mcp.example"
    assert outcome.success is True
    assert outcome.course_results[0].course_id == "7"
    assert outcome.metrics["provider"] == "foundry"


def test_foundry_orchestrator_requires_client():
    orchestrator = FoundryOrchestrator(client=None, mcp_endpoint="https://mcp.example")
    config = StudyGuideConfig(agent_provider="foundry", storage_provider="azure", task_prompt="sync")

    with pytest.raises(RuntimeError, match="Foundry client is not configured"):
        orchestrator.invoke("sync", config)
