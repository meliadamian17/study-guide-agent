from study_guide_agent.models import RunOutcome, StudyGuideConfig


class GeminiOrchestrator:
    """Gemini strategy with simple function-call orchestration loop."""

    def __init__(
        self,
        model_client: object | None = None,
        tools: dict[str, object] | None = None,
        max_steps: int = 8,
    ) -> None:
        self.model_client = model_client
        self.tools = tools or {}
        self.max_steps = max_steps

    def invoke(self, task_prompt: str, config: StudyGuideConfig) -> RunOutcome:
        if self.model_client is None:
            return RunOutcome(
                success=True,
                course_results=[],
                metrics={"provider": "gemini", "mode": "noop"},
            )

        transcript: list[dict] = []
        for _ in range(self.max_steps):
            response = self.model_client.generate(task_prompt, transcript)
            response_type = response.get("type")
            if response_type == "final":
                course_results = response.get("course_results", [])
                return RunOutcome(
                    success=True,
                    course_results=[
                        self._to_course_result(item) for item in course_results
                    ],
                    metrics={"provider": "gemini"},
                )

            if response_type == "function_call":
                tool_name = response["name"]
                arguments = response.get("arguments", {})
                tool = self.tools.get(tool_name)
                if tool is None:
                    raise KeyError(f"Unknown tool: {tool_name}")
                tool_result = tool(**arguments)
                transcript.append(
                    {
                        "tool_name": tool_name,
                        "arguments": arguments,
                        "result": tool_result,
                    }
                )
                continue

            raise RuntimeError(f"Unsupported model response type: {response_type}")

        raise RuntimeError("Max orchestration steps exceeded")

    @staticmethod
    def _to_course_result(raw: dict) -> object:
        from study_guide_agent.models import CourseResult

        return CourseResult(
            course_id=str(raw.get("course_id", "")),
            status=raw.get("status", "unknown"),
            guide_path=raw.get("guide_path"),
            error=raw.get("error"),
        )
