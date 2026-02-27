import os
from collections.abc import Callable
from typing import Any

from study_guide_agent.orchestrators.azure_openai import AzureOpenAIOrchestrator
from study_guide_agent.orchestrators.azure_openai_client import (
    create_azure_openai_client_from_env,
)
from study_guide_agent.orchestrators.protocol import AgentOrchestrator
from study_guide_agent.storage import create_storage
from study_guide_agent.tools.canvas_tools import CanvasTools


def build_study_guide_tools(
    canvas_tools: CanvasTools, storage: Any
) -> dict[str, Callable[..., Any]]:
    def write_study_guide(
        course_id: str, content: str, slug: str = "", meta: dict | None = None
    ) -> dict[str, Any]:
        path = storage.write_study_guide(
            course_id=str(course_id),
            slug=str(slug),
            content=str(content),
            meta=dict(meta or {}),
        )
        return {"path": path}

    return {
        "list_my_courses": lambda: canvas_tools.list_my_courses(),
        "list_modules": lambda course_id: canvas_tools.list_modules(course_id=str(course_id)),
        "get_module_items": lambda course_id, module_id: canvas_tools.get_module_items(
            course_id=str(course_id), module_id=str(module_id)
        ),
        "get_page_content": lambda course_id, page_url: canvas_tools.get_page_content(
            course_id=str(course_id), page_url=str(page_url)
        ),
        "get_file_content": lambda file_id: canvas_tools.get_file_content(file_id=str(file_id)),
        "list_announcements": lambda context_codes: canvas_tools.list_announcements(
            context_codes=list(context_codes)
        ),
        "list_assignments": lambda course_id: canvas_tools.list_assignments(course_id=str(course_id)),
        "write_study_guide": write_study_guide,
    }


def create_orchestrator(provider: str) -> AgentOrchestrator:
    normalized = provider.strip().lower()
    if normalized != "azure_openai":
        raise ValueError(f"Unknown agent provider: {provider}")

    model = os.getenv("AZURE_OPENAI_MODEL")
    if not model:
        raise RuntimeError("Missing AZURE_OPENAI_MODEL")
    storage_provider = os.getenv("STORAGE_PROVIDER", "azure")

    client = create_azure_openai_client_from_env()
    canvas_tools = CanvasTools(
        token=os.getenv("CANVAS_TOKEN", ""),
        base_url=os.getenv("CANVAS_BASE_URL", "https://q.utoronto.ca"),
    )
    storage = create_storage(storage_provider)
    tools = build_study_guide_tools(canvas_tools=canvas_tools, storage=storage)
    return AzureOpenAIOrchestrator(openai_client=client, model=model, tools=tools)


__all__ = [
    "AgentOrchestrator",
    "AzureOpenAIOrchestrator",
    "create_azure_openai_client_from_env",
    "build_study_guide_tools",
    "create_orchestrator",
]
