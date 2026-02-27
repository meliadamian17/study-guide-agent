from study_guide_agent.models import CourseResult, RunOutcome, StudyGuideConfig
from study_guide_agent.runner import StudyGuideRunner, load_config_from_env


class FakeStorage:
    def __init__(self) -> None:
        self.run_history = []

    def read_config(self) -> tuple[str, str]:
        return "# Template", "- Guideline"

    def write_study_guide(self, course_id: str, slug: str, content: str, meta: dict) -> str:
        return f"/tmp/{course_id}/study-guide.md"

    def write_run_history(self, run_id: str, summary: dict) -> str:
        self.run_history.append({"run_id": run_id, "summary": summary})
        return f"/tmp/runs/{run_id}.json"


class FakeOrchestrator:
    def __init__(self) -> None:
        self.invocations = []

    def invoke(self, task_prompt: str, config: StudyGuideConfig) -> RunOutcome:
        self.invocations.append({"task_prompt": task_prompt, "config": config})
        return RunOutcome(
            success=True,
            course_results=[CourseResult(course_id="1", status="updated")],
            metrics={"provider": config.agent_provider},
        )


def test_runner_invokes_orchestrator_with_loaded_template_guidelines():
    orchestrator = FakeOrchestrator()
    storage = FakeStorage()
    config = StudyGuideConfig(
        agent_provider="gemini",
        storage_provider="gcs",
        task_prompt="sync",
    )

    runner = StudyGuideRunner(orchestrator=orchestrator, storage=storage)
    outcome = runner.run(config)

    assert outcome.success is True
    assert len(orchestrator.invocations) == 1
    assert "Template" in orchestrator.invocations[0]["config"].task_prompt
    assert "Guideline" in orchestrator.invocations[0]["config"].task_prompt
    assert storage.run_history[0]["summary"]["success"] is True


def test_load_config_from_env_defaults(monkeypatch):
    monkeypatch.delenv("AGENT_PROVIDER", raising=False)
    monkeypatch.delenv("STORAGE_PROVIDER", raising=False)
    monkeypatch.delenv("TASK_PROMPT", raising=False)

    config = load_config_from_env()

    assert config.agent_provider == "gemini"
    assert config.storage_provider == "gcs"
    assert config.task_prompt == "Sync all courses and update study guides."


def test_load_config_from_env_uses_values(monkeypatch):
    monkeypatch.setenv("AGENT_PROVIDER", "foundry")
    monkeypatch.setenv("STORAGE_PROVIDER", "azure")
    monkeypatch.setenv("TASK_PROMPT", "custom prompt")

    config = load_config_from_env()

    assert config.agent_provider == "foundry"
    assert config.storage_provider == "azure"
    assert config.task_prompt == "custom prompt"
