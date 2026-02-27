from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class StudyGuideConfig:
    agent_provider: str
    storage_provider: str
    task_prompt: str
    course_filter: str | None = None
    run_id: str | None = None


@dataclass(frozen=True)
class CourseResult:
    course_id: str
    status: str
    guide_path: str | None = None
    error: str | None = None


@dataclass(frozen=True)
class RunOutcome:
    success: bool
    course_results: list[CourseResult] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
