# Quercus Study Guide Agent

Provider-agnostic study guide runner for Quercus (Canvas) with strategy-based orchestration and storage.

Foundry-first stage now includes:

- Expanded `CanvasTools` endpoint coverage aligned to Canvas docs
- MCP server scaffold for Azure Functions (`mcp_server/`)
- Env-driven Foundry client wiring in orchestrator factory

## What this does

- Pulls course data via shared Canvas tools.
- Orchestrates runs with either:
  - `gemini` strategy (`GeminiOrchestrator`)
  - `foundry` strategy (`FoundryOrchestrator`)
- Stores study guide artifacts with either:
  - `gcs` strategy (`GCSStorage`)
  - `azure` strategy (`AzureBlobStorage`)
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

## Runtime configuration

Set environment variables before running:

- `AGENT_PROVIDER`: `gemini` (default) or `foundry`
- `STORAGE_PROVIDER`: `gcs` (default) or `azure`
- `TASK_PROMPT`: override default sync prompt
- `COURSE_FILTER`: optional filter expression
- `RUN_ID`: optional explicit run identifier
- `CANVAS_BASE_URL`: default `https://q.utoronto.ca`
- `CANVAS_TOKEN`: required for Canvas API calls
- `MCP_SERVER_URL`: required for Foundry orchestrator tool connectivity
- `FOUNDRY_ENDPOINT`: `https://<resource>.services.ai.azure.com`
- `FOUNDRY_PROJECT`: Foundry project name
- `FOUNDRY_APP`: Foundry app name
- `FOUNDRY_MODEL`: optional model override (default `gpt-4.1`)
- `FOUNDRY_API_VERSION`: optional API version override

## Canvas API references used for CanvasTools

- Schema/auth/pagination: [Canvas schema](https://developerdocs.instructure.com/services/canvas#schema)
- Courses: [Courses API](https://developerdocs.instructure.com/services/canvas/resources/courses#method.courses.index)
- Modules: [Modules API](https://developerdocs.instructure.com/services/canvas/resources/modules#method.context_modules_api.index)
- Pages: [Pages API](https://developerdocs.instructure.com/services/canvas/resources/pages#method.wiki_pages_api.show)
- Files: [Files API](https://developerdocs.instructure.com/services/canvas/resources/files)
- Announcements: [Announcements API](https://developerdocs.instructure.com/services/canvas/resources/announcements#method.announcements_api.index)
- Assignments: [Assignments API](https://developerdocs.instructure.com/services/canvas/resources/assignments)

## Foundry + MCP quick start

1. Configure env vars (Canvas + Foundry + MCP).
2. Deploy `mcp_server/` to Azure Functions.
3. Register MCP server in Foundry and attach tool calls.
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
