import pytest

from study_guide_agent.models import StudyGuideConfig
from study_guide_agent.orchestrators.gemini import GeminiOrchestrator


class FakeModelClient:
    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    def generate(self, prompt: str, transcript: list[dict]) -> dict:
        self.calls.append({"prompt": prompt, "transcript": list(transcript)})
        return self._responses.pop(0)


def test_gemini_orchestrator_dispatches_tool_then_returns_outcome():
    calls = []

    def list_courses():
        calls.append("list_courses")
        return [{"id": "1"}]

    model = FakeModelClient(
        [
            {"type": "function_call", "name": "list_courses", "arguments": {}},
            {"type": "final", "course_results": [{"course_id": "1", "status": "updated"}]},
        ]
    )
    orchestrator = GeminiOrchestrator(model_client=model, tools={"list_courses": list_courses})
    config = StudyGuideConfig(agent_provider="gemini", storage_provider="gcs", task_prompt="sync")

    outcome = orchestrator.invoke("sync", config)

    assert calls == ["list_courses"]
    assert outcome.success is True
    assert len(outcome.course_results) == 1
    assert outcome.course_results[0].course_id == "1"


def test_gemini_orchestrator_raises_for_unknown_tool():
    model = FakeModelClient([{"type": "function_call", "name": "missing", "arguments": {}}])
    orchestrator = GeminiOrchestrator(model_client=model, tools={})
    config = StudyGuideConfig(agent_provider="gemini", storage_provider="gcs", task_prompt="sync")

    with pytest.raises(KeyError, match="Unknown tool"):
        orchestrator.invoke("sync", config)


def test_gemini_orchestrator_stops_after_max_steps():
    model = FakeModelClient([{"type": "function_call", "name": "noop", "arguments": {}}] * 5)
    orchestrator = GeminiOrchestrator(
        model_client=model, tools={"noop": lambda: None}, max_steps=2
    )
    config = StudyGuideConfig(agent_provider="gemini", storage_provider="gcs", task_prompt="sync")

    with pytest.raises(RuntimeError, match="Max orchestration steps exceeded"):
        orchestrator.invoke("sync", config)
