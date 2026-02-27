# Manual Steps (Foundry-First Rollout)

This checklist documents everything you need to do manually after the code changes.

## 1) Quercus / Canvas token

1. Sign in to `https://q.utoronto.ca`.
2. Create an access token from Canvas account settings (or use your institution's OAuth flow).
3. Store token securely (Key Vault for Azure deployment).
4. Do not commit tokens into repository files.

API reference for auth and schema:

- Canvas Schema + Auth: [Canvas schema](https://developerdocs.instructure.com/services/canvas#schema)

## 2) Verify Canvas permissions and endpoint coverage

Confirm your token has access needed for:

- Courses: `GET /api/v1/courses`
- Modules: `GET /api/v1/courses/:course_id/modules`
- Module items: `GET /api/v1/courses/:course_id/modules/:module_id/items`
- Pages: `GET /api/v1/courses/:course_id/pages/:url_or_id`
- Files: `GET /api/v1/files/:id` and file download URL
- Announcements: `GET /api/v1/announcements`
- Assignments: `GET /api/v1/courses/:course_id/assignments`

Docs:

- Courses: [Courses API](https://developerdocs.instructure.com/services/canvas/resources/courses#method.courses.index)
- Modules: [Modules API](https://developerdocs.instructure.com/services/canvas/resources/modules#method.context_modules_api.index)
- Pages: [Pages API](https://developerdocs.instructure.com/services/canvas/resources/pages#method.wiki_pages_api.show)
- Files: [Files API](https://developerdocs.instructure.com/services/canvas/resources/files)
- Announcements: [Announcements API](https://developerdocs.instructure.com/services/canvas/resources/announcements#method.announcements_api.index)
- Assignments: [Assignments API](https://developerdocs.instructure.com/services/canvas/resources/assignments)

## 3) Local environment setup

1. Activate virtualenv:
   - `source venv/bin/activate`
2. Install/refresh dependencies:
   - `pip install -e ".[dev,azure]"`
3. Set env vars:
   - `CANVAS_BASE_URL=https://q.utoronto.ca`
   - `CANVAS_TOKEN=<your_token>`
   - `AGENT_PROVIDER=foundry`
   - `STORAGE_PROVIDER=azure`
   - `MCP_SERVER_URL=<your_mcp_url>`
   - `FOUNDRY_ENDPOINT=https://<resource>.services.ai.azure.com`
   - `FOUNDRY_PROJECT=<project_name>`
   - `FOUNDRY_APP=<app_name>`
   - optional: `FOUNDRY_MODEL=gpt-4.1`
   - optional: `FOUNDRY_API_VERSION=2025-11-15-preview`

## 4) Azure Foundry setup

1. Create an Azure AI Foundry project and application.
2. Deploy MCP server endpoint (Azure Functions recommended).
3. Register MCP server in Foundry so agent can call tools.
4. Ensure identity/authentication path works (Entra ID recommended).

## 5) MCP server deployment

Project scaffold exists in `mcp_server/`.

1. Create Function App resource.
2. Deploy contents of `mcp_server/`.
3. Configure Function App settings:
   - `CANVAS_BASE_URL`
   - `CANVAS_TOKEN`
   - `STORAGE_PROVIDER=azure`
4. Verify HTTP route is reachable (`/api/mcp/tools` by default Function route convention).

## 6) Storage preparation

For production Azure storage, create containers or equivalent prefixes:

- `config/` (template + guidelines)
- `study-guides/` (per-course output)
- `runs/` (run history summaries)

Upload:

- `study-guide-template.md`
- `guidelines.md`

## 7) Scheduling

Pick one:

- Azure Function timer trigger
- Logic App scheduled trigger

Suggested cron: `0 0 2 * * *` (2:00 AM daily, adjust timezone as needed).

## 8) Operational checks

1. Run tests:
   - `venv/bin/python -m pytest`
2. Trigger one manual run.
3. Confirm:
   - Study guides written per course
   - `runs/<run_id>.json` exists
   - No authentication or rate-limit failures in logs

## 9) First production run checklist

- [ ] Canvas token valid
- [ ] Foundry env vars set
- [ ] MCP URL reachable from Foundry
- [ ] Template/guidelines uploaded
- [ ] One dry run completed successfully
