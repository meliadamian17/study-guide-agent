import os
from typing import Any

from study_guide_agent.storage import create_storage
from study_guide_agent.tools.canvas_tools import CanvasTools


class CanvasToolsHandler:
    """
    MCP tool dispatcher around CanvasTools and study-guide storage.
    """

    def __init__(
        self,
        canvas_tools: CanvasTools | None = None,
        storage: Any | None = None,
    ) -> None:
        self.canvas_tools = canvas_tools or CanvasTools(
            token=os.getenv("CANVAS_TOKEN", ""),
            base_url=os.getenv("CANVAS_BASE_URL", "https://q.utoronto.ca"),
        )
        self.storage = storage or create_storage(os.getenv("STORAGE_PROVIDER", "azure"))
        self._tools = {
            "list_my_courses": lambda args: self.canvas_tools.list_my_courses(),
            "list_modules": lambda args: self.canvas_tools.list_modules(
                course_id=str(args["course_id"])
            ),
            "get_module_items": lambda args: self.canvas_tools.get_module_items(
                course_id=str(args["course_id"]),
                module_id=str(args["module_id"]),
            ),
            "get_page_content": lambda args: self.canvas_tools.get_page_content(
                course_id=str(args["course_id"]),
                page_url=str(args["page_url"]),
            ),
            "get_file_content": lambda args: self.canvas_tools.get_file_content(
                file_id=str(args["file_id"])
            ),
            "list_announcements": lambda args: self.canvas_tools.list_announcements(
                context_codes=list(args["context_codes"])
            ),
            "list_assignments": lambda args: self.canvas_tools.list_assignments(
                course_id=str(args["course_id"])
            ),
            "write_study_guide": self._write_study_guide,
        }

    def list_tools(self) -> list[str]:
        return sorted(self._tools.keys())

    def dispatch(self, tool_name: str, args: dict[str, Any]) -> Any:
        callback = self._tools.get(tool_name)
        if callback is None:
            raise KeyError(f"Unknown MCP tool: {tool_name}")
        return callback(args)

    def _write_study_guide(self, args: dict[str, Any]) -> dict[str, Any]:
        output_path = self.storage.write_study_guide(
            course_id=str(args["course_id"]),
            slug=str(args.get("slug", "")),
            content=str(args["content"]),
            meta=dict(args.get("meta", {})),
        )
        return {"path": output_path}
