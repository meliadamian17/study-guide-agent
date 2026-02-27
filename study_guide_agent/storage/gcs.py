import json
from pathlib import Path


class GCSStorage:
    """
    Local filesystem-backed placeholder for GCS strategy.
    """

    def __init__(self, base_dir: str = "runtime_storage/gcs") -> None:
        self.base_path = Path(base_dir)
        self.config_path = self.base_path / "config"
        self.guides_path = self.base_path / "study-guides"
        self.runs_path = self.base_path / "runs"
        self.config_path.mkdir(parents=True, exist_ok=True)
        self.guides_path.mkdir(parents=True, exist_ok=True)
        self.runs_path.mkdir(parents=True, exist_ok=True)

    def read_config(self) -> tuple[str, str]:
        template_file = self.config_path / "study-guide-template.md"
        guidelines_file = self.config_path / "guidelines.md"
        template = template_file.read_text() if template_file.exists() else ""
        guidelines = guidelines_file.read_text() if guidelines_file.exists() else ""
        return template, guidelines

    def write_study_guide(
        self, course_id: str, slug: str, content: str, meta: dict
    ) -> str:
        course_dir = self.guides_path / course_id
        course_dir.mkdir(parents=True, exist_ok=True)
        guide_path = course_dir / "study-guide.md"
        guide_path.write_text(content)
        meta_path = course_dir / "course-meta.json"
        meta_path.write_text(json.dumps(meta))
        return str(guide_path)

    def write_run_history(self, run_id: str, summary: dict) -> str:
        output_path = self.runs_path / f"{run_id}.json"
        output_path.write_text(json.dumps(summary))
        return str(output_path)
