import json
from types import SimpleNamespace

from study_guide_agent.models import StudyGuideConfig
from study_guide_agent.orchestrators.azure_openai import AzureOpenAIOrchestrator


class FakeCompletions:
    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return self._responses.pop(0)


class FakeClient:
    def __init__(self, responses):
        self.chat = SimpleNamespace(completions=FakeCompletions(responses))


def _tool_call(call_id: str, name: str, arguments: dict):
    return SimpleNamespace(
        id=call_id,
        function=SimpleNamespace(name=name, arguments=json.dumps(arguments)),
    )


def _response_with_tool_calls(*calls):
    message = SimpleNamespace(tool_calls=list(calls), content=None)
    choice = SimpleNamespace(message=message)
    return SimpleNamespace(choices=[choice])


def _response_final(text: str):
    message = SimpleNamespace(tool_calls=None, content=text)
    choice = SimpleNamespace(message=message)
    return SimpleNamespace(choices=[choice])


def test_orchestrator_invokes_tools_and_infers_course_results():
    called = []

    def list_my_courses():
        called.append("list_my_courses")
        return [{"id": "1", "name": "Course"}]

    def write_study_guide(course_id, content, slug="", meta=None):
        called.append("write_study_guide")
        assert course_id == "1"
        return {"path": "/tmp/1/study-guide.md"}

    client = FakeClient(
        [
            _response_with_tool_calls(_tool_call("tc1", "list_my_courses", {})),
            _response_with_tool_calls(
                _tool_call(
                    "tc2",
                    "write_study_guide",
                    {"course_id": "1", "content": "# Guide", "slug": "", "meta": {}},
                )
            ),
            _response_final("Done."),
        ]
    )
    orchestrator = AzureOpenAIOrchestrator(
        openai_client=client,
        model="kimi-k2.5",
        tools={
            "list_my_courses": list_my_courses,
            "write_study_guide": write_study_guide,
        },
    )
    config = StudyGuideConfig(
        agent_provider="azure_openai", storage_provider="azure", task_prompt="sync"
    )

    outcome = orchestrator.invoke("Sync", config)

    assert called == ["list_my_courses", "write_study_guide"]
    assert outcome.success is True
    assert len(outcome.course_results) == 1
    assert outcome.course_results[0].course_id == "1"
    assert outcome.course_results[0].guide_path == "/tmp/1/study-guide.md"
    assert outcome.metrics["provider"] == "azure_openai"
