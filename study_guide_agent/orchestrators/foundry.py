from study_guide_agent.models import RunOutcome, StudyGuideConfig


class FoundryOrchestrator:
    """Foundry strategy adapter around a client.run(payload) call."""

    def __init__(self, client: object | None = None, mcp_endpoint: str | None = None) -> None:
        self.client = client
        self.mcp_endpoint = mcp_endpoint

    def invoke(self, task_prompt: str, config: StudyGuideConfig) -> RunOutcome:
        if self.client is None:
            raise RuntimeError("Foundry client is not configured")

        payload = {
            "prompt": task_prompt,
            "task_prompt": config.task_prompt,
            "mcp_endpoint": self.mcp_endpoint,
        }
        response = self.client.run(payload)
        metrics = dict(response.get("metrics", {}))
        metrics["provider"] = "foundry"

        from study_guide_agent.models import CourseResult

        course_results = [
            CourseResult(
                course_id=str(item.get("course_id", "")),
                status=item.get("status", "unknown"),
                guide_path=item.get("guide_path"),
                error=item.get("error"),
            )
            for item in response.get("course_results", [])
        ]
        return RunOutcome(success=True, course_results=course_results, metrics=metrics)
