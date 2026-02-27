import os

from study_guide_agent.orchestrators import create_orchestrator


def test_create_orchestrator_foundry_uses_env_wiring(monkeypatch):
    monkeypatch.setenv("MCP_SERVER_URL", "https://mcp.example")
    monkeypatch.setenv("FOUNDRY_ENDPOINT", "https://resource.services.ai.azure.com")
    monkeypatch.setenv("FOUNDRY_PROJECT", "proj")
    monkeypatch.setenv("FOUNDRY_APP", "app")

    created = {"called": False}

    class FakeClient:
        def run(self, payload):
            return {"course_results": [], "metrics": {}}

    def fake_create():
        created["called"] = True
        return FakeClient()

    monkeypatch.setattr(
        "study_guide_agent.orchestrators.create_foundry_client_from_env", fake_create
    )

    orchestrator = create_orchestrator("foundry")

    assert created["called"] is True
    assert orchestrator.mcp_endpoint == "https://mcp.example"


def test_create_orchestrator_foundry_missing_env_raises(monkeypatch):
    monkeypatch.delenv("FOUNDRY_ENDPOINT", raising=False)
    monkeypatch.delenv("FOUNDRY_PROJECT", raising=False)
    monkeypatch.delenv("FOUNDRY_APP", raising=False)

    def fake_create():
        raise RuntimeError("Missing Foundry env vars")

    monkeypatch.setattr(
        "study_guide_agent.orchestrators.create_foundry_client_from_env", fake_create
    )

    try:
        create_orchestrator("foundry")
        raised = False
    except RuntimeError as exc:
        raised = "Missing Foundry env vars" in str(exc)

    assert raised is True
