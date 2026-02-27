# Manual Steps (Model-Only Azure Rollout)

This checklist is for the current architecture: model-only orchestration in-process (no Foundry agents and no MCP server).

## 1) Quercus / Canvas token

1. Sign in to `https://q.utoronto.ca`.
2. Create an access token in Canvas account settings.
3. Store the token in Azure Key Vault.
4. Do not commit tokens in repository files.

## 2) Verify Canvas permissions

Confirm token access for:

- `GET /api/v1/courses`
- `GET /api/v1/courses/:course_id/modules`
- `GET /api/v1/courses/:course_id/modules/:module_id/items`
- `GET /api/v1/courses/:course_id/pages/:url_or_id`
- `GET /api/v1/files/:id`
- `GET /api/v1/announcements`
- `GET /api/v1/courses/:course_id/assignments`

## 3) Deploy model in Azure AI Foundry (UI only)

1. Open [Azure AI Foundry](https://ai.azure.com) and your project.
2. Go to **Models** / **Deployments**.
3. Deploy **Kimi K2.5**.
4. Record:
   - Endpoint: `https://<resource>.services.ai.azure.com/openai/v1/`
   - Deployment name (used as `AZURE_OPENAI_MODEL`)
5. Ensure your identity has role **Cognitive Services OpenAI User** on the resource.

## 4) Configure storage (Azure Blob, UI only)

1. Create or open a storage account.
2. Create containers:
   - `config`
   - `study-guides`
   - `runs`
3. Upload to `config` (canonical files are in `config/` at project root):
   - `study-guide-template.md` — structure: key definitions, concepts, examples, practice questions, diagrams, references
   - `guidelines.md` — rules: no detail omitted, diagrams in Mermaid, cite all source material
4. Grant the runner identity **Storage Blob Data Contributor**.

## 5) Runner environment variables

Set these where the runner executes:

- `AGENT_PROVIDER=azure_openai`
- `STORAGE_PROVIDER=azure`
- `CANVAS_BASE_URL=https://q.utoronto.ca`
- `CANVAS_TOKEN=<token or Key Vault reference>`
- `AZURE_OPENAI_ENDPOINT=https://<resource>.services.ai.azure.com/openai/v1/`
- `AZURE_OPENAI_MODEL=<kimi-k2.5 deployment name>`
- optional: `AZURE_OPENAI_API_KEY=<key>` (not needed with Entra ID)
- optional: `TASK_PROMPT=<override>`
- optional: `COURSE_FILTER=<filter>`
- optional: `RUN_ID=<explicit id>`

## 6) Run and verify

1. Run tests: `venv/bin/python -m pytest`
2. Run the app: `venv/bin/python -m study_guide_agent`
3. Verify outputs:
   - Study guides are written per course.
   - Run summary file exists in `runs/`.
   - No auth or rate-limit errors in logs.

## 7) First production run checklist

- [ ] Kimi K2.5 deployment is healthy
- [ ] `AZURE_OPENAI_ENDPOINT` and `AZURE_OPENAI_MODEL` are correct
- [ ] Canvas token is valid
- [ ] Config files are uploaded
- [ ] One dry run completed successfully
