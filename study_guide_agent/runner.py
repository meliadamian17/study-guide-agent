import os
from datetime import UTC, datetime

from study_guide_agent.models import RunOutcome, StudyGuideConfig
from study_guide_agent.orchestrators import create_orchestrator
from study_guide_agent.orchestrators.protocol import AgentOrchestrator, StudyGuideStorage
from study_guide_agent.storage import create_storage


def load_config_from_env() -> StudyGuideConfig:
    return StudyGuideConfig(
        agent_provider=os.getenv("AGENT_PROVIDER", "gemini"),
        storage_provider=os.getenv("STORAGE_PROVIDER", "gcs"),
        task_prompt=os.getenv(
            "TASK_PROMPT", "Sync all courses and update study guides."
        ),
        course_filter=os.getenv("COURSE_FILTER"),
        run_id=os.getenv("RUN_ID"),
    )


class StudyGuideRunner:
    def __init__(
        self,
        orchestrator: AgentOrchestrator | None = None,
        storage: StudyGuideStorage | None = None,
    ) -> None:
        self.orchestrator = orchestrator
        self.storage = storage

    def run(self, config: StudyGuideConfig) -> RunOutcome:
        orchestrator = self.orchestrator or create_orchestrator(config.agent_provider)
        storage = self.storage or create_storage(config.storage_provider)

        template, guidelines = storage.read_config()
        compiled_prompt = self._compose_prompt(config.task_prompt, template, guidelines)
        effective_config = StudyGuideConfig(
            agent_provider=config.agent_provider,
            storage_provider=config.storage_provider,
            task_prompt=compiled_prompt,
            course_filter=config.course_filter,
            run_id=config.run_id,
        )
        outcome = orchestrator.invoke(compiled_prompt, effective_config)

        run_id = config.run_id or datetime.now(tz=UTC).strftime("%Y%m%dT%H%M%SZ")
        summary = {
            "success": outcome.success,
            "course_count": len(outcome.course_results),
            "errors": len([c for c in outcome.course_results if c.error]),
            "provider": config.agent_provider,
        }
        storage.write_run_history(run_id=run_id, summary=summary)
        return outcome

    @staticmethod
    def _compose_prompt(base_prompt: str, template: str, guidelines: str) -> str:
        parts = [base_prompt]
        if template:
            parts.append(f"Template:\n{template}")
        if guidelines:
            parts.append(f"Guidelines:\n{guidelines}")
        return "\n\n".join(parts)
