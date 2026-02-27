import httpx
import pytest

from study_guide_agent.tools.canvas_tools import CanvasTools


def test_list_my_courses_handles_pagination():
    page_1 = [{"id": 1, "name": "A"}, {"id": 2, "name": "B"}]
    page_2 = [{"id": 3, "name": "C"}]

    def handler(request: httpx.Request) -> httpx.Response:
        if "page=2" in str(request.url):
            return httpx.Response(200, json=page_2)
        link = '<https://quercus.example/api/v1/courses?page=2>; rel="next"'
        return httpx.Response(200, json=page_1, headers={"Link": link})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    tools = CanvasTools(base_url="https://quercus.example", token="t", client=client)

    courses = tools.list_my_courses()

    assert [c["id"] for c in courses] == [1, 2, 3]


def test_list_modules_retries_on_429_then_succeeds():
    attempts = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        attempts["count"] += 1
        if attempts["count"] == 1:
            return httpx.Response(429, json={"error": "throttled"})
        return httpx.Response(200, json=[{"id": 11, "name": "Module"}])

    client = httpx.Client(transport=httpx.MockTransport(handler))
    tools = CanvasTools(
        base_url="https://quercus.example",
        token="t",
        client=client,
        max_retries=2,
        backoff_seconds=0.0,
    )

    modules = tools.list_modules(course_id="42")
    assert modules == [{"id": 11, "name": "Module"}]
    assert attempts["count"] == 2


def test_list_modules_raises_after_retry_exhausted():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, json={"error": "still throttled"})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    tools = CanvasTools(
        base_url="https://quercus.example",
        token="t",
        client=client,
        max_retries=1,
        backoff_seconds=0.0,
    )

    with pytest.raises(httpx.HTTPStatusError):
        tools.list_modules(course_id="42")
