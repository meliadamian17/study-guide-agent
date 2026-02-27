import json
from collections.abc import Callable
from typing import Any

from study_guide_agent.models import CourseResult, RunOutcome, StudyGuideConfig
from study_guide_agent.tools.openai_schemas import get_openai_tool_definitions


class AzureOpenAIOrchestrator:
    """Model-only OpenAI tool-calling loop for Azure-hosted deployments."""

    def __init__(
        self,
        openai_client: object,
        model: str,
        tools: dict[str, Callable[..., Any]],
        max_steps: int = 10,
    ) -> None:
        self.openai_client = openai_client
        self.model = model
        self.tools = tools
        self.max_steps = max_steps
        self.tool_definitions = get_openai_tool_definitions()

    def invoke(self, task_prompt: str, config: StudyGuideConfig) -> RunOutcome:
        messages: list[dict[str, Any]] = [{"role": "user", "content": task_prompt}]
        guide_paths: dict[str, str] = {}
        final_text = ""
        steps = 0

        for steps in range(1, self.max_steps + 1):
            response = self.openai_client.chat.completions.create(
                model=self.model, messages=messages, tools=self.tool_definitions
            )
            message = response.choices[0].message
            tool_calls = getattr(message, "tool_calls", None)

            if not tool_calls:
                final_text = getattr(message, "content", "") or ""
                break

            assistant_tool_calls: list[dict[str, Any]] = []
            for call in tool_calls:
                assistant_tool_calls.append(
                    {
                        "id": call.id,
                        "type": "function",
                        "function": {
                            "name": call.function.name,
                            "arguments": call.function.arguments,
                        },
                    }
                )
            messages.append({"role": "assistant", "tool_calls": assistant_tool_calls})

            for call in tool_calls:
                tool_name = call.function.name
                args_text = call.function.arguments or "{}"
                args = json.loads(args_text)
                tool = self.tools.get(tool_name)
                if tool is None:
                    raise KeyError(f"Unknown tool: {tool_name}")
                result = tool(**args)

                if tool_name == "write_study_guide":
                    course_id = str(args.get("course_id", ""))
                    if course_id:
                        if isinstance(result, dict):
                            guide_paths[course_id] = str(result.get("path", ""))
                        else:
                            guide_paths[course_id] = str(result)

                serialized_result = (
                    json.dumps(result) if not isinstance(result, str) else result
                )
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": serialized_result,
                    }
                )
        else:
            raise RuntimeError("Max orchestration steps exceeded")

        course_results = [
            CourseResult(course_id=cid, status="updated", guide_path=path or None)
            for cid, path in sorted(guide_paths.items())
        ]
        return RunOutcome(
            success=True,
            course_results=course_results,
            metrics={
                "provider": config.agent_provider,
                "model": self.model,
                "steps": steps,
                "output_text_length": len(final_text),
            },
        )
