import json
import os
from pathlib import Path
from typing import Optional

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

CONTAINER_CONFIG = "config"
CONTAINER_GUIDES = "study-guides"
CONTAINER_RUNS = "runs"


def _blob_service_client() -> BlobServiceClient | None:
    conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if conn_str:
        return BlobServiceClient.from_connection_string(conn_str)
    account_url = os.getenv("AZURE_STORAGE_ACCOUNT_URL")
    if not account_url:
        return None
    url = account_url.strip().rstrip("/")
    if not url.startswith("http"):
        url = f"https://{url}.blob.core.windows.net"
    credential = DefaultAzureCredential()
    return BlobServiceClient(account_url=url, credential=credential)


class AzureBlobStorage:
    """
    Azure Blob Storage adapter. Uses containers: config, study-guides, runs.
    Falls back to local filesystem when no storage env vars are set (for tests/local dev).
    """

    def __init__(
        self,
        blob_service_client: Optional[BlobServiceClient] = None,
        base_dir: str = "runtime_storage/azure",
    ) -> None:
        client: Optional[BlobServiceClient] = blob_service_client or _blob_service_client()
        if client is not None:
            self._client: Optional[BlobServiceClient] = client
            self._base_path: Optional[Path] = None
        else:
            self._client = None
            self._base_path = Path(base_dir)
            self._base_path.mkdir(parents=True, exist_ok=True)

    def read_config(self) -> tuple[str, str]:
        if self._client is not None:
            config_container = self._client.get_container_client(CONTAINER_CONFIG)
            template = self._download_text(
                config_container, "study-guide-template.md"
            )
            guidelines = self._download_text(config_container, "guidelines.md")
            return template, guidelines
        base = self._base_path
        if base is None:
            raise RuntimeError("Storage not configured")
        config_path = base / "config"
        config_path.mkdir(parents=True, exist_ok=True)
        template_file = config_path / "study-guide-template.md"
        guidelines_file = config_path / "guidelines.md"
        template = template_file.read_text() if template_file.exists() else ""
        guidelines = guidelines_file.read_text() if guidelines_file.exists() else ""
        return template, guidelines

    def write_study_guide(
        self, course_id: str, slug: str, content: str, meta: dict
    ) -> str:
        if self._client is not None:
            guides_container = self._client.get_container_client(CONTAINER_GUIDES)
            guide_blob = f"{course_id}/study-guide.md"
            meta_blob = f"{course_id}/course-meta.json"
            self._upload_text(guides_container, guide_blob, content)
            self._upload_text(
                guides_container, meta_blob, json.dumps(meta)
            )
            return f"{CONTAINER_GUIDES}/{guide_blob}"
        base = self._base_path
        if base is None:
            raise RuntimeError("Storage not configured")
        guides_path = base / "study-guides" / course_id
        guides_path.mkdir(parents=True, exist_ok=True)
        (guides_path / "study-guide.md").write_text(content)
        (guides_path / "course-meta.json").write_text(json.dumps(meta))
        return str(guides_path / "study-guide.md")

    def write_run_history(self, run_id: str, summary: dict) -> str:
        if self._client is not None:
            runs_container = self._client.get_container_client(CONTAINER_RUNS)
            blob_name = f"{run_id}.json"
            self._upload_text(runs_container, blob_name, json.dumps(summary))
            return f"{CONTAINER_RUNS}/{blob_name}"
        base = self._base_path
        if base is None:
            raise RuntimeError("Storage not configured")
        runs_path = base / "runs"
        runs_path.mkdir(parents=True, exist_ok=True)
        output_path = runs_path / f"{run_id}.json"
        output_path.write_text(json.dumps(summary))
        return str(output_path)

    @staticmethod
    def _download_text(container_client, blob_name: str) -> str:
        try:
            blob_client = container_client.get_blob_client(blob_name)
            data = blob_client.download_blob().readall()
            return data.decode("utf-8")
        except Exception:
            return ""

    @staticmethod
    def _upload_text(container_client, blob_name: str, content: str) -> None:
        blob_client = container_client.get_blob_client(blob_name)
        blob_client.upload_blob(content.encode("utf-8"), overwrite=True)
