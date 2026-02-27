import base64

import httpx

from study_guide_agent.tools.canvas_tools import QUERCUS_BASE_URL, CanvasTools


def test_canvas_tools_default_base_url():
    client = httpx.Client(transport=httpx.MockTransport(lambda _: httpx.Response(200, json=[])))
    tools = CanvasTools(token="token", client=client)
    assert tools.base_url == QUERCUS_BASE_URL


def test_list_my_courses_uses_canvas_course_filters_and_headers():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["auth"] = request.headers.get("Authorization")
        captured["accept"] = request.headers.get("Accept")
        return httpx.Response(200, json=[{"id": "1"}])

    tools = CanvasTools(token="token", client=httpx.Client(transport=httpx.MockTransport(handler)))
    result = tools.list_my_courses()

    assert result == [{"id": "1"}]
    assert "enrollment_type=student" in captured["url"]
    assert "enrollment_state=active" in captured["url"]
    assert captured["auth"] == "Bearer token"
    assert captured["accept"] == "application/json+canvas-string-ids"


def test_list_modules_requests_items_and_content_details():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        return httpx.Response(200, json=[{"id": "11", "items": []}])

    tools = CanvasTools(token="token", client=httpx.Client(transport=httpx.MockTransport(handler)))
    result = tools.list_modules(course_id="42")

    assert result == [{"id": "11", "items": []}]
    assert "include%5B%5D=items" in captured["url"]
    assert "include%5B%5D=content_details" in captured["url"]


def test_get_module_items_uses_paginated_endpoint():
    page_1 = [{"id": "a"}]
    page_2 = [{"id": "b"}]

    def handler(request: httpx.Request) -> httpx.Response:
        if "page=2" in str(request.url):
            return httpx.Response(200, json=page_2)
        link = '<https://q.utoronto.ca/api/v1/courses/42/modules/7/items?page=2>; rel="next"'
        return httpx.Response(200, json=page_1, headers={"Link": link})

    tools = CanvasTools(token="token", client=httpx.Client(transport=httpx.MockTransport(handler)))
    items = tools.get_module_items(course_id="42", module_id="7")

    assert items == [{"id": "a"}, {"id": "b"}]


def test_get_page_content_returns_page_object():
    def handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url).endswith("/api/v1/courses/42/pages/week-1")
        return httpx.Response(200, json={"title": "Week 1", "body": "<p>Hello</p>"})

    tools = CanvasTools(token="token", client=httpx.Client(transport=httpx.MockTransport(handler)))
    page = tools.get_page_content(course_id="42", page_url="week-1")

    assert page["title"] == "Week 1"
    assert page["body"] == "<p>Hello</p>"


def test_get_file_content_fetches_metadata_then_relative_download_url():
    calls = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["count"] += 1
        if calls["count"] == 1:
            assert str(request.url).endswith("/api/v1/files/99")
            return httpx.Response(
                200,
                json={
                    "id": "99",
                    "display_name": "notes.txt",
                    "content-type": "text/plain",
                    "url": "/files/99/download?download_frd=1&verifier=abc",
                },
            )
        assert str(request.url).startswith("https://q.utoronto.ca/files/99/download")
        return httpx.Response(200, content=b"important text")

    tools = CanvasTools(token="token", client=httpx.Client(transport=httpx.MockTransport(handler)))
    file_obj = tools.get_file_content(file_id="99")

    assert file_obj["id"] == "99"
    assert file_obj["name"] == "notes.txt"
    assert file_obj["encoding"] == "text"
    assert file_obj["content"] == "important text"


def test_get_file_content_returns_base64_for_binary_data():
    calls = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["count"] += 1
        if calls["count"] == 1:
            return httpx.Response(
                200,
                json={
                    "id": "100",
                    "display_name": "slides.pdf",
                    "content-type": "application/pdf",
                    "url": "https://q.utoronto.ca/files/100/download?download_frd=1&verifier=xyz",
                },
            )
        return httpx.Response(200, content=b"\xff\x00\x11")

    tools = CanvasTools(token="token", client=httpx.Client(transport=httpx.MockTransport(handler)))
    file_obj = tools.get_file_content(file_id="100")

    assert file_obj["encoding"] == "base64"
    assert file_obj["content"] == base64.b64encode(b"\xff\x00\x11").decode("ascii")


def test_list_announcements_sends_context_codes_array():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        return httpx.Response(200, json=[{"id": "500", "context_code": "course_42"}])

    tools = CanvasTools(token="token", client=httpx.Client(transport=httpx.MockTransport(handler)))
    result = tools.list_announcements(context_codes=["course_42", "course_99"])

    assert result[0]["id"] == "500"
    assert "context_codes%5B%5D=course_42" in captured["url"]
    assert "context_codes%5B%5D=course_99" in captured["url"]


def test_list_assignments_is_paginated():
    page_1 = [{"id": "a1"}]
    page_2 = [{"id": "a2"}]

    def handler(request: httpx.Request) -> httpx.Response:
        if "page=2" in str(request.url):
            return httpx.Response(200, json=page_2)
        link = '<https://q.utoronto.ca/api/v1/courses/42/assignments?page=2>; rel="next"'
        return httpx.Response(200, json=page_1, headers={"Link": link})

    tools = CanvasTools(token="token", client=httpx.Client(transport=httpx.MockTransport(handler)))
    result = tools.list_assignments(course_id="42")

    assert result == [{"id": "a1"}, {"id": "a2"}]
