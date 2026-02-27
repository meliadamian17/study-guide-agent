from typing import Protocol, runtime_checkable

from study_guide_agent.models import RunOutcome, StudyGuideConfig


@runtime_checkable
class AgentOrchestrator(Protocol):
    """Strategy protocol for provider-specific orchestration."""

    def invoke(self, task_prompt: str, config: StudyGuideConfig) -> RunOutcome:
        ...


@runtime_checkable
class StudyGuideStorage(Protocol):
    """Strategy protocol for study guide storage providers."""

    def read_config(self) -> tuple[str, str]:
        ...

    def write_study_guide(
        self, course_id: str, slug: str, content: str, meta: dict
    ) -> str:
        ...

    def write_run_history(self, run_id: str, summary: dict) -> str:
        ...
