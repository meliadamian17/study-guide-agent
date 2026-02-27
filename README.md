# Quercus Study Guide Agent

Model-only study guide runner for Quercus (Canvas) with strategy-based storage.

Current architecture:

- Expanded `CanvasTools` endpoint coverage aligned to Canvas docs
- Azure OpenAI-compatible orchestration loop with in-process tool calling
- Azure-first storage strategy (`AzureBlobStorage`)

## What this does

- Pulls course data via `CanvasTools`.
- Orchestrates runs with `azure_openai` strategy (`AzureOpenAIOrchestrator`).
- Stores study guide artifacts with either:
  - `azure` strategy (`AzureBlobStorage`)
  - `gcs` strategy (`GCSStorage`)
- Writes run history metadata per execution.

## How to interact with it

### 1) Scheduled mode (recommended)

Deploy the runner and schedule it:

- Azure: Azure Function timer trigger.
- GCP: Cloud Scheduler -> Cloud Function or Cloud Run.

Your laptop does not need to stay online after deployment.

### 2) Manual cloud trigger

Expose an HTTP endpoint in your function host and trigger a run by POSTing to it.

### 3) Manual local run

Use your virtualenv interpreter:

```bash
venv/bin/python -m study_guide_agent
```

## Runtime Configuration

Set environment variables before running:

- `AGENT_PROVIDER`: `azure_openai` (default)
- `STORAGE_PROVIDER`: `azure` (default) or `gcs`
- `TASK_PROMPT`: override default sync prompt
- `COURSE_FILTER`: optional filter expression
- `RUN_ID`: optional explicit run identifier
- `CANVAS_BASE_URL`: default `https://q.utoronto.ca`
- `CANVAS_TOKEN`: required for Canvas API calls
- `AZURE_OPENAI_ENDPOINT`: `https://<resource>.services.ai.azure.com/openai/v1/`
- `AZURE_OPENAI_MODEL`: deployment name (for this rollout: Kimi K2.5 deployment)
- `AZURE_OPENAI_API_KEY`: optional (if unset, Entra ID via `DefaultAzureCredential` is used)

## Canvas API references used for CanvasTools

- Schema/auth/pagination: [Canvas schema](https://developerdocs.instructure.com/services/canvas#schema)
- Courses: [Courses API](https://developerdocs.instructure.com/services/canvas/resources/courses#method.courses.index)
- Modules: [Modules API](https://developerdocs.instructure.com/services/canvas/resources/modules#method.context_modules_api.index)
- Pages: [Pages API](https://developerdocs.instructure.com/services/canvas/resources/pages#method.wiki_pages_api.show)
- Files: [Files API](https://developerdocs.instructure.com/services/canvas/resources/files)
- Announcements: [Announcements API](https://developerdocs.instructure.com/services/canvas/resources/announcements#method.announcements_api.index)
- Assignments: [Assignments API](https://developerdocs.instructure.com/services/canvas/resources/assignments)

## Azure Model-Only Quick Start

1. Deploy model in Azure AI Foundry (Kimi K2.5).
2. Set `AZURE_OPENAI_ENDPOINT` and `AZURE_OPENAI_MODEL`.
3. Set Canvas credentials and storage provider.
4. Run:

```bash
venv/bin/python -m study_guide_agent
```

For full deployment/operator runbook, see `docs/MANUAL_STEPS.md`.

## Where results go

Current storage adapters use filesystem-backed layout with cloud-equivalent paths:

```text
runtime_storage/{provider}/
  config/
    study-guide-template.md
    guidelines.md
  study-guides/
    {course_id}/
      study-guide.md
      course-meta.json
  runs/
    {run_id}.json
```

`provider` is `gcs` or `azure`.

## Viewing results

- Open `study-guides/{course_id}/study-guide.md` for each course.
- Inspect `runs/{run_id}.json` for run-level status and metrics summary.

In real cloud deployments, map these paths to:

- Azure Blob containers: `config`, `study-guides`, `runs`
- GCS buckets/prefixes: `config`, `study-guides`, `runs`
