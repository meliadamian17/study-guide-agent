import json
from pathlib import Path

from study_guide_agent.storage.azure_blob import AzureBlobStorage
from study_guide_agent.storage.gcs import GCSStorage


def _seed_config(base: Path) -> None:
    config = base / "config"
    config.mkdir(parents=True, exist_ok=True)
    (config / "study-guide-template.md").write_text("# Template")
    (config / "guidelines.md").write_text("- Keep concise")


def test_azure_blob_storage_reads_template_and_guidelines(tmp_path: Path):
    base = tmp_path / "azure"
    _seed_config(base)

    storage = AzureBlobStorage(base_dir=str(base))
    template, guidelines = storage.read_config()

    assert template == "# Template"
    assert guidelines == "- Keep concise"


def test_gcs_storage_writes_study_guide_and_json_meta(tmp_path: Path):
    base = tmp_path / "gcs"
    storage = GCSStorage(base_dir=str(base))

    path = storage.write_study_guide(
        course_id="1234",
        slug="course-slug",
        content="Guide body",
        meta={"course_name": "CSC101", "items": 12},
    )

    guide_path = Path(path)
    assert guide_path.exists()
    assert guide_path.read_text() == "Guide body"

    meta_path = base / "study-guides" / "1234" / "course-meta.json"
    assert json.loads(meta_path.read_text()) == {"course_name": "CSC101", "items": 12}


def test_azure_blob_storage_writes_run_history_json(tmp_path: Path):
    base = tmp_path / "azure"
    storage = AzureBlobStorage(base_dir=str(base))

    run_path = storage.write_run_history(
        run_id="run-123",
        summary={"success": True, "course_count": 4, "errors": 0},
    )

    output = Path(run_path)
    assert output.exists()
    assert output.name == "run-123.json"
    assert json.loads(output.read_text()) == {
        "success": True,
        "course_count": 4,
        "errors": 0,
    }
