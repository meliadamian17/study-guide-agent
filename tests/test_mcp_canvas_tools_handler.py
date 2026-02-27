import pytest

from mcp_server.tools.canvas_tools_handler import CanvasToolsHandler


class FakeCanvasTools:
    def list_my_courses(self):
        return [{"id": "1"}]

    def list_modules(self, course_id: str):
        return [{"id": "m1", "course_id": course_id}]

    def get_module_items(self, course_id: str, module_id: str):
        return [{"id": "it1", "course_id": course_id, "module_id": module_id}]

    def get_page_content(self, course_id: str, page_url: str):
        return {"course_id": course_id, "url": page_url, "body": "<p>x</p>"}

    def get_file_content(self, file_id: str):
        return {"id": file_id, "encoding": "text", "content": "abc"}

    def list_announcements(self, context_codes: list[str]):
        return [{"id": "a1", "context_code": context_codes[0]}]

    def list_assignments(self, course_id: str):
        return [{"id": "as1", "course_id": course_id}]


class FakeStorage:
    def __init__(self):
        self.calls = []

    def write_study_guide(self, course_id: str, slug: str, content: str, meta: dict) -> str:
        self.calls.append((course_id, slug, content, meta))
        return f"/tmp/{course_id}/study-guide.md"


def test_dispatch_canvas_methods_and_write_study_guide():
    handler = CanvasToolsHandler(canvas_tools=FakeCanvasTools(), storage=FakeStorage())

    assert handler.dispatch("list_my_courses", {}) == [{"id": "1"}]
    assert handler.dispatch("list_modules", {"course_id": "42"}) == [
        {"id": "m1", "course_id": "42"}
    ]
    assert handler.dispatch(
        "get_module_items", {"course_id": "42", "module_id": "7"}
    ) == [{"id": "it1", "course_id": "42", "module_id": "7"}]
    assert handler.dispatch("get_page_content", {"course_id": "42", "page_url": "week-1"})[
        "url"
    ] == "week-1"
    assert handler.dispatch("get_file_content", {"file_id": "99"})["id"] == "99"
    assert handler.dispatch(
        "list_announcements", {"context_codes": ["course_42"]}
    )[0]["context_code"] == "course_42"
    assert handler.dispatch("list_assignments", {"course_id": "42"})[0]["id"] == "as1"

    output = handler.dispatch(
        "write_study_guide",
        {
            "course_id": "42",
            "slug": "course-42",
            "content": "# Guide",
            "meta": {"items": 10},
        },
    )
    assert output["path"].endswith("/42/study-guide.md")


def test_dispatch_unknown_tool_raises():
    handler = CanvasToolsHandler(canvas_tools=FakeCanvasTools(), storage=FakeStorage())
    with pytest.raises(KeyError, match="Unknown MCP tool"):
        handler.dispatch("nope", {})
