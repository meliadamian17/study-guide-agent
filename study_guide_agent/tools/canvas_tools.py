import base64
import time
from typing import Any
from urllib.parse import urljoin

import httpx

QUERCUS_BASE_URL = "https://q.utoronto.ca"


class CanvasTools:
    """Canvas API helper with pagination and basic retry handling."""

    def __init__(
        self,
        token: str,
        base_url: str = QUERCUS_BASE_URL,
        client: httpx.Client | None = None,
        max_retries: int = 3,
        backoff_seconds: float = 0.2,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds
        self.client = client or httpx.Client()

    def list_my_courses(self) -> list[dict[str, Any]]:
        return self._get_paginated(
            "/api/v1/courses",
            params={"enrollment_type": "student", "enrollment_state": "active"},
        )

    def list_modules(self, course_id: str) -> list[dict[str, Any]]:
        include_values = ["items", "content_details"]
        return self._get_paginated(
            f"/api/v1/courses/{course_id}/modules",
            params={"include[]": include_values},
        )

    def get_module_items(self, course_id: str, module_id: str) -> list[dict[str, Any]]:
        return self._get_paginated(
            f"/api/v1/courses/{course_id}/modules/{module_id}/items"
        )

    def get_page_content(self, course_id: str, page_url: str) -> dict[str, Any]:
        return self._get_json(f"/api/v1/courses/{course_id}/pages/{page_url}")

    def get_file_content(self, file_id: str) -> dict[str, Any]:
        metadata = self._get_json(f"/api/v1/files/{file_id}")
        download_url = metadata.get("url")
        if not download_url:
            raise ValueError("File metadata missing download url")

        absolute_download_url = urljoin(self.base_url + "/", str(download_url))
        response = self._request("GET", absolute_download_url)
        raw = response.content
        mime_type = metadata.get("content-type", "application/octet-stream")
        name = metadata.get("display_name") or metadata.get("filename") or str(file_id)

        try:
            text = raw.decode("utf-8")
            encoding = "text"
            content: str = text
        except UnicodeDecodeError:
            encoding = "base64"
            content = base64.b64encode(raw).decode("ascii")

        return {
            "id": str(metadata.get("id", file_id)),
            "name": name,
            "mime_type": mime_type,
            "encoding": encoding,
            "content": content,
        }

    def list_announcements(self, context_codes: list[str]) -> list[dict[str, Any]]:
        return self._get_paginated(
            "/api/v1/announcements",
            params={"context_codes[]": context_codes},
        )

    def list_assignments(self, course_id: str) -> list[dict[str, Any]]:
        return self._get_paginated(f"/api/v1/courses/{course_id}/assignments")

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json+canvas-string-ids",
        }

    def _request(
        self, method: str, url: str, params: dict[str, Any] | None = None
    ) -> httpx.Response:
        for attempt in range(self.max_retries + 1):
            response = self.client.request(
                method=method,
                url=url,
                params=params,
                headers=self._headers(),
                timeout=30.0,
            )
            if response.status_code != 429:
                response.raise_for_status()
                return response
            if attempt == self.max_retries:
                response.raise_for_status()
            delay = self.backoff_seconds * (2**attempt)
            if delay > 0:
                time.sleep(delay)
        raise RuntimeError("retry loop exhausted")

    def _get_json(
        self, path: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        response = self._request("GET", f"{self.base_url}{path}", params=params)
        payload = response.json()
        if not isinstance(payload, dict):
            raise TypeError("Expected JSON object response")
        return payload

    def _get_paginated(
        self, path: str, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        next_url: str = f"{self.base_url}{path}"
        next_params = params
        while next_url:
            response = self._request("GET", next_url, params=next_params)
            payload = response.json()
            if isinstance(payload, list):
                items.extend(payload)
            next_url = response.links.get("next", {}).get("url")
            next_params = None
        return items
