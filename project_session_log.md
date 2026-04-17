# Project Session Log

Append-only log for thread handoff. Add one new entry at the end of the file after each substantive session.

## Entry Template

### Session YYYY-MM-DD - short title

- Scope:
- Main changes:
- Verification:
- Outstanding follow-ups:
- Files touched:

## Session 2026-04-08 - Full-text workspace fixes and handoff structure

- Scope: fixed full-text queue source labeling and dataset-scoping bugs, then formalized the cross-thread handoff workflow
- Main changes:
  - corrected full-text round labels to use screening rounds sorted by creation time
  - added loading and error feedback for queue rebuild, OA/link refresh, and status-save actions
  - changed backend dataset validation to resolve derived datasets inside the current project instead of using global dataset-id lookup
  - added a regression test for project-scoped `cumulative-included`
  - rebuilt `E:\wenxian\project_state.md` into a strict summary template
  - created this append-only session log
- Verification:
  - `cd E:\wenxian\literature_screening_web && npm run typecheck`
  - `cd E:\wenxian\literature_screening_web && npm run build`
  - `cd E:\wenxian\literature_screening && python -m pytest literature_screening/tests/test_api_app.py -k "fulltext_queue_rebuild_and_status_update or project_scoped_cumulative_dataset"`
- Outstanding follow-ups:
  - keep checking for any remaining full-text page UX that still looks silent
  - decide later whether the session log needs a stronger checklist or can stay lightweight
- Files touched:
  - `E:\wenxian\literature_screening_web\src\views\FulltextQueueView.vue`
  - `E:\wenxian\literature_screening\src\literature_screening\api\app.py`
  - `E:\wenxian\literature_screening\tests\test_api_app.py`
  - `E:\wenxian\project_state.md`
  - `E:\wenxian\project_session_log.md`

## Session 2026-04-08 - Thread data migration helpers

- Scope: identified where persisted thread data lives and added helper scripts for exporting it to another machine
- Main changes:
  - confirmed thread and task state is stored under `E:\wenxian\literature_screening\data\api_runs`
  - added `E:\wenxian\scripts\export-api-runs.py` to export either the full `api_runs` tree or selected projects with related tasks
  - added `E:\wenxian\scripts\repair-api-runs-paths.py` to rewrite stored absolute paths after moving data from Windows to macOS
  - updated the handoff summary to mention the migration helpers
- Verification:
  - `cd E:\wenxian && python -m py_compile scripts\export-api-runs.py scripts\repair-api-runs-paths.py`
- Outstanding follow-ups:
  - add an optional import wrapper later if the Mac mini migration flow needs to be even more automated
  - if path portability becomes a recurring issue, move persisted metadata from absolute paths to repo-relative paths
- Files touched:
  - `E:\wenxian\scripts\export-api-runs.py`
  - `E:\wenxian\scripts\repair-api-runs-paths.py`
  - `E:\wenxian\project_state.md`
  - `E:\wenxian\project_session_log.md`

## Session 2026-04-09 - Mac local runtime and relative path persistence

- Scope: moved active development onto the Mac local Docker setup, imported Windows runtime data, and eliminated persisted absolute-path coupling by switching `api_runs` storage to relative paths
- Main changes:
  - synced the local repository to the latest GitHub `main` before continuing work
  - imported Windows `wenxian-api-runs` data into `/Users/mao/Documents/langchain/literature_screening/data/api_runs`
  - improved `/Users/mao/Documents/langchain/scripts/repair-api-runs-paths.py` during the migration work so JSON and YAML rewrites are safer
  - added local macOS start and stop helpers with `/Users/mao/Documents/langchain/start-wenxian.command`, `/Users/mao/Documents/langchain/stop-wenxian.command`, `/Users/mao/Documents/langchain/docker-compose.local.yml`, and `/Users/mao/Documents/langchain/literature_screening_web/deploy/nginx.local.conf`
  - updated `/Users/mao/Documents/langchain/literature_screening/Dockerfile` so the backend image builds reliably for local Docker use
  - diagnosed the full-text queue reset after report generation as a host-path versus container-path mismatch in persisted metadata
  - added `/Users/mao/Documents/langchain/literature_screening/src/literature_screening/storage_paths.py` and routed task, dataset, and screening-config persistence through it so disk format is now relative to `api_runs`
  - added `/Users/mao/Documents/langchain/scripts/relativize-api-runs-paths.py` and migrated existing `api_runs` data to relative paths
  - added regression coverage for path dehydration and hydration in `/Users/mao/Documents/langchain/literature_screening/tests/test_task_store.py` and `/Users/mao/Documents/langchain/literature_screening/tests/test_api_app.py`
  - created the reusable Codex handoff skill at `/Users/mao/.codex/skills/project-handoff-sync/SKILL.md`
- Verification:
  - `PYTHONPATH=/Users/mao/Documents/langchain/literature_screening/src ./.venv/bin/python -m pytest literature_screening/tests/test_task_store.py literature_screening/tests/test_api_app.py`
  - `./.venv/bin/python -m compileall literature_screening/src/literature_screening/storage_paths.py literature_screening/src/literature_screening/api/task_store.py literature_screening/src/literature_screening/api/workspace_store.py literature_screening/src/literature_screening/core/config.py literature_screening/src/literature_screening/studio/service.py literature_screening/src/literature_screening/api/app.py scripts/relativize-api-runs-paths.py literature_screening/tests/test_task_store.py literature_screening/tests/test_api_app.py`
  - `./.venv/bin/python scripts/relativize-api-runs-paths.py --api-runs-root /Users/mao/Documents/langchain/literature_screening/data/api_runs`
  - `docker compose -f /Users/mao/Documents/langchain/docker-compose.local.yml up -d --build api`
  - `docker compose -f /Users/mao/Documents/langchain/docker-compose.local.yml ps`
  - `curl http://127.0.0.1:8000/api/health`
- Outstanding follow-ups:
  - decide later whether the API should expose stored-relative paths as well as resolved absolute paths
  - extend `storage_paths.py` if future persisted files introduce new path-like keys
  - consider whether the older Windows-path entries in this log should ever be backfilled, or should remain as historical context only
- Files touched:
  - `/Users/mao/Documents/langchain/literature_screening/src/literature_screening/storage_paths.py`
  - `/Users/mao/Documents/langchain/literature_screening/src/literature_screening/api/app.py`
  - `/Users/mao/Documents/langchain/literature_screening/src/literature_screening/api/task_store.py`
  - `/Users/mao/Documents/langchain/literature_screening/src/literature_screening/api/workspace_store.py`
  - `/Users/mao/Documents/langchain/literature_screening/src/literature_screening/core/config.py`
  - `/Users/mao/Documents/langchain/literature_screening/src/literature_screening/studio/service.py`
  - `/Users/mao/Documents/langchain/literature_screening/tests/test_task_store.py`
  - `/Users/mao/Documents/langchain/literature_screening/tests/test_api_app.py`
  - `/Users/mao/Documents/langchain/scripts/repair-api-runs-paths.py`
  - `/Users/mao/Documents/langchain/scripts/relativize-api-runs-paths.py`
  - `/Users/mao/Documents/langchain/literature_screening/Dockerfile`
  - `/Users/mao/Documents/langchain/docker-compose.local.yml`
  - `/Users/mao/Documents/langchain/literature_screening_web/deploy/nginx.local.conf`
  - `/Users/mao/Documents/langchain/start-wenxian.command`
  - `/Users/mao/Documents/langchain/stop-wenxian.command`
  - `/Users/mao/Documents/langchain/project_state.md`
  - `/Users/mao/Documents/langchain/project_session_log.md`
  - `/Users/mao/.codex/skills/project-handoff-sync/SKILL.md`

## Session 2026-04-09 - API dual path compatibility fields

- Scope: evaluated whether the API should expose both absolute and stored-relative paths, then implemented the compatibility fields for dataset and task-detail responses
- Main changes:
  - added `relative_path` to dataset API responses while keeping the existing absolute `path`
  - added `run_root_relative` and `output_dir_relative` to task-detail responses while keeping the existing absolute fields
  - kept server-side runtime logic on hydrated absolute paths so review, report, and artifact flows do not need to change
  - updated frontend TypeScript response types to accept the new relative-path fields
  - added API regression tests covering both dataset and task-detail dual-path responses
- Verification:
  - `PYTHONPATH=/Users/mao/Documents/langchain/literature_screening/src ./.venv/bin/python -m pytest /Users/mao/Documents/langchain/literature_screening/tests/test_api_app.py -k 'relative_path or relative_task_paths or relative-path or dataset_api_returns_absolute_and_relative_paths or task_detail_api_returns_absolute_and_relative_task_paths or workspace_store_persists_dataset_paths_relatively or load_run_config_resolves_api_runs_relative_paths_from_storage_root'`
  - `PYTHONPATH=/Users/mao/Documents/langchain/literature_screening/src ./.venv/bin/python -m pytest /Users/mao/Documents/langchain/literature_screening/tests/test_api_app.py`
- Outstanding follow-ups:
  - decide when external callers and the web UI should start preferring the new relative-path fields over absolute-path assumptions
  - rerun frontend `typecheck` once a Node/npm toolchain is available on this machine
- Files touched:
  - `/Users/mao/Documents/langchain/literature_screening/src/literature_screening/api/app.py`
  - `/Users/mao/Documents/langchain/literature_screening/src/literature_screening/api/schemas.py`
  - `/Users/mao/Documents/langchain/literature_screening/tests/test_api_app.py`
  - `/Users/mao/Documents/langchain/literature_screening_web/src/types/api.ts`
  - `/Users/mao/Documents/langchain/project_state.md`
  - `/Users/mao/Documents/langchain/project_session_log.md`

## Session 2026-04-09 - Documentation refresh for current workflow

- Scope: refreshed the public-facing docs so GitHub-facing usage notes match the current Docker-first local runtime and thread-first product shape
- Main changes:
  - rewrote the root `README.md` to describe the current startup flow, data layout, and path-compatibility behavior
  - updated `literature_screening/docs/architecture.md` to reflect strategy tasks, full-text workflow, `storage_paths.py`, and relative-path persistence
  - updated `literature_screening/docs/web-workbench.md` to reflect current routes, full-text page, Docker startup, and API surface
  - updated `literature_screening/separated_modules/formal_report_module/README.md` to document current simple/formal report entry points and module boundaries
- Verification:
  - `git diff --check README.md literature_screening/docs/architecture.md literature_screening/docs/web-workbench.md literature_screening/separated_modules/formal_report_module/README.md`
- Outstanding follow-ups:
  - if the Web UI starts consuming the new relative-path fields directly, update the web-workbench doc again to note that shift explicitly
  - the nested `literature_screening/README.md` still contains older environment notes and can be refreshed later if needed
- Files touched:
  - `/Users/mao/Documents/langchain/README.md`
  - `/Users/mao/Documents/langchain/literature_screening/docs/architecture.md`
  - `/Users/mao/Documents/langchain/literature_screening/docs/web-workbench.md`
  - `/Users/mao/Documents/langchain/literature_screening/separated_modules/formal_report_module/README.md`
  - `/Users/mao/Documents/langchain/project_state.md`
  - `/Users/mao/Documents/langchain/project_session_log.md`

## Session 2026-04-09 - Final handoff sync and Windows startup clarification

- Scope: finalized the branch handoff for the next thread and clarified that Windows uses the same local Docker compose flow even though the one-click scripts are macOS-only
- Main changes:
  - updated the root `README.md` to distinguish macOS `.command` launchers from Windows manual `docker compose -f docker-compose.local.yml up -d --build`
  - refreshed `project_state.md` to reflect the active branch `codex/relative-path-api-compat` and latest pushed commit `cc462c9`
  - noted that the remaining workspace noise is local untracked environment artifacts rather than tracked project changes
- Verification:
  - `git diff --check README.md`
  - `git status --short --branch`
- Outstanding follow-ups:
  - add Windows PowerShell start/stop wrappers later if manual Docker startup is too inconvenient
  - refresh `literature_screening/README.md` later so nested docs match the root README
- Files touched:
  - `/Users/mao/Documents/langchain/README.md`
  - `/Users/mao/Documents/langchain/project_state.md`
  - `/Users/mao/Documents/langchain/project_session_log.md`

## Session 2026-04-09 - Thread-first workflow redesign and persisted thread context

- Scope: reworked the main interaction flow so threads are created from a fuzzy research need, thread defaults persist on the backend, screening inherits thread context, and reporting is explicitly moved behind full-text acquisition
- Main changes:
  - added persisted `thread_profile` data to project metadata in `/Users/mao/Documents/langchain/literature_screening/src/literature_screening/api/workspace_store.py` and exposed it through `/Users/mao/Documents/langchain/literature_screening/src/literature_screening/api/schemas.py`
  - extended `/Users/mao/Documents/langchain/literature_screening/src/literature_screening/api/app.py` so strategy generation writes back thread-level research need, selected databases, generated plan, and default screening topic/criteria
  - added `/api/projects/{project_id}/workflow` for editing fixed thread context and `/api/tasks/{task_id}/review-overrides/selection` for direct multi-select review actions
  - turned `/Users/mao/Documents/langchain/literature_screening_web/src/views/StrategyRunView.vue` into the new `/threads/new` kickoff page focused on research need, provider/model, and database selection
  - redesigned `/Users/mao/Documents/langchain/literature_screening_web/src/views/ProjectDetailView.vue` around a fixed thread-context header plus four stages: thread plan, screening, full text, report
  - simplified `/Users/mao/Documents/langchain/literature_screening_web/src/views/ScreeningRunView.vue` so it emphasizes thread/source selection, file input, thread-default criteria, and minimal run settings
  - updated `/Users/mao/Documents/langchain/literature_screening_web/src/components/ScreeningRecordsTable.vue` and `/Users/mao/Documents/langchain/literature_screening_web/src/views/TaskDetailView.vue` so screening review now supports multi-select actions plus year filter and year sorting
  - removed direct report creation from screening task detail and made the thread/report UI depend on `fulltext_ready` data instead
- Verification:
  - `PYTHONPATH=/Users/mao/Documents/langchain/literature_screening/src ./.venv/bin/python -m pytest literature_screening/tests/test_api_app.py -q`
  - `./.venv/bin/python -m compileall literature_screening/src/literature_screening/api/app.py literature_screening/src/literature_screening/api/schemas.py literature_screening/src/literature_screening/api/workspace_store.py literature_screening/tests/test_api_app.py`
  - `docker run --rm -v /Users/mao/Documents/langchain/literature_screening_web:/work -w /work node:20 sh -lc 'npm ci >/tmp/npm-ci.log && npm run build >/tmp/npm-build.log && cat /tmp/npm-build.log'`
  - `git diff --check literature_screening/src/literature_screening/api/app.py literature_screening/src/literature_screening/api/schemas.py literature_screening/src/literature_screening/api/workspace_store.py literature_screening/tests/test_api_app.py literature_screening_web/src/api/client.ts literature_screening_web/src/components/ScreeningRecordsTable.vue literature_screening_web/src/layouts/AppShell.vue literature_screening_web/src/router/index.ts literature_screening_web/src/stores/drafts.ts literature_screening_web/src/stores/projects.ts literature_screening_web/src/stores/tasks.ts literature_screening_web/src/types/api.ts literature_screening_web/src/utils/strategy.ts literature_screening_web/src/views/DashboardView.vue literature_screening_web/src/views/ProjectDetailView.vue literature_screening_web/src/views/ScreeningRunView.vue literature_screening_web/src/views/StrategyRunView.vue literature_screening_web/src/views/TaskDetailView.vue`
- Outstanding follow-ups:
  - consider whether to write a one-off migration that materializes derived `thread_profile` data into all older project JSON files
  - investigate frontend bundle-size warnings later if production chunking starts to matter
  - refresh `/Users/mao/Documents/langchain/literature_screening/README.md` so nested docs match the new thread-first flow
- Files touched:
  - `/Users/mao/Documents/langchain/literature_screening/src/literature_screening/api/app.py`
  - `/Users/mao/Documents/langchain/literature_screening/src/literature_screening/api/schemas.py`
  - `/Users/mao/Documents/langchain/literature_screening/src/literature_screening/api/workspace_store.py`
  - `/Users/mao/Documents/langchain/literature_screening/tests/test_api_app.py`
  - `/Users/mao/Documents/langchain/literature_screening_web/src/api/client.ts`
  - `/Users/mao/Documents/langchain/literature_screening_web/src/components/ScreeningRecordsTable.vue`
  - `/Users/mao/Documents/langchain/literature_screening_web/src/layouts/AppShell.vue`
  - `/Users/mao/Documents/langchain/literature_screening_web/src/router/index.ts`
  - `/Users/mao/Documents/langchain/literature_screening_web/src/stores/drafts.ts`
  - `/Users/mao/Documents/langchain/literature_screening_web/src/stores/projects.ts`
  - `/Users/mao/Documents/langchain/literature_screening_web/src/stores/tasks.ts`
  - `/Users/mao/Documents/langchain/literature_screening_web/src/types/api.ts`
  - `/Users/mao/Documents/langchain/literature_screening_web/src/utils/strategy.ts`
  - `/Users/mao/Documents/langchain/literature_screening_web/src/views/DashboardView.vue`
  - `/Users/mao/Documents/langchain/literature_screening_web/src/views/ProjectDetailView.vue`
  - `/Users/mao/Documents/langchain/literature_screening_web/src/views/ScreeningRunView.vue`
  - `/Users/mao/Documents/langchain/literature_screening_web/src/views/StrategyRunView.vue`
  - `/Users/mao/Documents/langchain/literature_screening_web/src/views/TaskDetailView.vue`
  - `/Users/mao/Documents/langchain/project_state.md`
  - `/Users/mao/Documents/langchain/project_session_log.md`

## Session 2026-04-09 - Hot-reload local development mode

- Scope: removed the need to rebuild the whole local stack for routine UI and API edits by adding a separate Dockerized development mode with source mounts and automatic reload
- Main changes:
  - added `/Users/mao/Documents/langchain/docker-compose.dev.yml` with bind-mounted backend source plus `uvicorn --reload`
  - added `/Users/mao/Documents/langchain/start-wenxian-dev.command` and `/Users/mao/Documents/langchain/stop-wenxian-dev.command` for one-click dev startup on macOS
  - updated `/Users/mao/Documents/langchain/literature_screening_web/vite.config.ts` so Dockerized Vite can use env-configured API proxy, polling watch mode, and HMR client port
  - updated `/Users/mao/Documents/langchain/start-wenxian.command` and `/Users/mao/Documents/langchain/stop-wenxian.command` to separate stable mode from dev mode and avoid port-conflict confusion
  - refreshed `/Users/mao/Documents/langchain/README.md` and handoff notes so the two runtime modes are documented for the next thread
- Verification:
  - `docker compose -p literature-screening-dev -f /Users/mao/Documents/langchain/docker-compose.dev.yml up -d`
  - `curl http://127.0.0.1:8000/api/health`
  - `curl http://127.0.0.1:8080`
  - `docker compose -p literature-screening-dev -f /Users/mao/Documents/langchain/docker-compose.dev.yml logs --tail=80 web`
  - `git diff --check README.md docker-compose.dev.yml start-wenxian.command stop-wenxian.command start-wenxian-dev.command stop-wenxian-dev.command literature_screening_web/vite.config.ts project_state.md project_session_log.md`
- Outstanding follow-ups:
  - if local Node is installed later, decide whether to keep Dockerized Vite as the default dev path or move hot-update work back to host tooling
  - if Windows convenience becomes important, add matching PowerShell wrappers for the new dev runtime
- Files touched:
  - `/Users/mao/Documents/langchain/docker-compose.dev.yml`
  - `/Users/mao/Documents/langchain/start-wenxian.command`
  - `/Users/mao/Documents/langchain/stop-wenxian.command`
  - `/Users/mao/Documents/langchain/start-wenxian-dev.command`
  - `/Users/mao/Documents/langchain/stop-wenxian-dev.command`
  - `/Users/mao/Documents/langchain/literature_screening_web/vite.config.ts`
  - `/Users/mao/Documents/langchain/README.md`
  - `/Users/mao/Documents/langchain/project_state.md`
  - `/Users/mao/Documents/langchain/project_session_log.md`

## Session 2026-04-09 - Thread-scoped plan and screening entry cleanup

- Scope: removed duplicate thread selection from thread-internal plan/screening flows and added clearer return-to-thread navigation from child pages
- Main changes:
  - added thread-scoped frontend routes for plan refresh and screening kickoff under `/threads/:projectId/plan/new` and `/threads/:projectId/screening/new`
  - updated `/Users/mao/Documents/langchain/literature_screening_web/src/views/ProjectDetailView.vue` so thread actions always launch thread-internal plan and screening pages instead of the generic global entry
  - updated `/Users/mao/Documents/langchain/literature_screening_web/src/views/StrategyRunView.vue` so refreshing a plan from inside a thread no longer shows an extra thread selector and instead presents the current thread as fixed context
  - updated `/Users/mao/Documents/langchain/literature_screening_web/src/views/ScreeningRunView.vue` so thread-internal screening no longer allows implicit new-thread creation, shows the current thread context, and provides direct return-to-thread buttons
  - updated `/Users/mao/Documents/langchain/literature_screening_web/src/views/TaskDetailView.vue`, `/Users/mao/Documents/langchain/literature_screening_web/src/layouts/AppShell.vue`, and `/Users/mao/Documents/langchain/literature_screening_web/src/views/DashboardView.vue` so drafts and task pages route back into the owning thread instead of bouncing users through a global picker
- Verification:
  - `docker compose -p literature-screening-dev -f /Users/mao/Documents/langchain/docker-compose.dev.yml exec -T web npm run build`
  - `git diff --check literature_screening_web/src/router/index.ts literature_screening_web/src/views/ProjectDetailView.vue literature_screening_web/src/views/TaskDetailView.vue literature_screening_web/src/views/StrategyRunView.vue literature_screening_web/src/views/ScreeningRunView.vue literature_screening_web/src/layouts/AppShell.vue literature_screening_web/src/views/DashboardView.vue`
- Outstanding follow-ups:
  - decide later whether the generic `/screening/new` route should stay as a lightweight global picker or be replaced by a dedicated thread chooser page
  - consider adding the same explicit “返回线程主页” affordance to any future standalone report-edit pages if report interactions move back out of the thread homepage
- Files touched:
  - `/Users/mao/Documents/langchain/literature_screening_web/src/router/index.ts`
  - `/Users/mao/Documents/langchain/literature_screening_web/src/views/ProjectDetailView.vue`
  - `/Users/mao/Documents/langchain/literature_screening_web/src/views/TaskDetailView.vue`
  - `/Users/mao/Documents/langchain/literature_screening_web/src/views/StrategyRunView.vue`
  - `/Users/mao/Documents/langchain/literature_screening_web/src/views/ScreeningRunView.vue`
  - `/Users/mao/Documents/langchain/literature_screening_web/src/layouts/AppShell.vue`
  - `/Users/mao/Documents/langchain/literature_screening_web/src/views/DashboardView.vue`
  - `/Users/mao/Documents/langchain/project_state.md`
  - `/Users/mao/Documents/langchain/project_session_log.md`

## Session 2026-04-09 - Confidence-first review order and merged full-text review stage

- Scope: made screening review prioritize relevance, then folded more of the final manual curation into the full-text workspace instead of keeping it conceptually separate
- Main changes:
  - updated `/Users/mao/Documents/langchain/literature_screening_web/src/components/ScreeningRecordsTable.vue` so screening records default to confidence-first ordering and keep confidence as the tie-breaker inside each year bucket
  - extended `/Users/mao/Documents/langchain/literature_screening/src/literature_screening/api/schemas.py`, `/Users/mao/Documents/langchain/literature_screening/src/literature_screening/api/workspace_store.py`, and `/Users/mao/Documents/langchain/literature_screening/src/literature_screening/api/app.py` so full-text queue items now carry screening confidence/reason context and support a dedicated `excluded` status
  - updated `/Users/mao/Documents/langchain/literature_screening_web/src/views/FulltextQueueView.vue` to act as “全文获取与最终复核工作台”, including relevance-aware sorting, displayed screening rationale, and a direct “复审排除” action
  - updated `/Users/mao/Documents/langchain/literature_screening_web/src/views/ProjectDetailView.vue` and `/Users/mao/Documents/langchain/literature_screening_web/src/views/TaskDetailView.vue` so the main workflow now points users toward the merged full-text/final-review stage, while keeping task-detail review tools as advanced optional fixes
  - updated `/Users/mao/Documents/langchain/literature_screening/src/literature_screening/core/models.py`, `/Users/mao/Documents/langchain/literature_screening/src/literature_screening/bibtex/parser.py`, `/Users/mao/Documents/langchain/literature_screening/src/literature_screening/bibtex/deduper.py`, and `/Users/mao/Documents/langchain/literature_screening/src/literature_screening/bibtex/exporter.py` so imported URL fields are preserved end-to-end and can be reused as landing links when DOI is missing
  - updated `/Users/mao/Documents/langchain/literature_screening_web/src/layouts/AppShell.vue` and `/Users/mao/Documents/langchain/literature_screening_web/src/views/DashboardView.vue` so the global copy consistently frames the flow as initial screening -> full-text review -> report
  - added regression coverage in `/Users/mao/Documents/langchain/literature_screening/tests/test_api_app.py` for confidence propagation into the full-text queue, the new `excluded` status, and imported-URL fallback when DOI is absent
- Verification:
  - `PYTHONPATH=/Users/mao/Documents/langchain/literature_screening/src ./.venv/bin/python -m pytest /Users/mao/Documents/langchain/literature_screening/tests/test_api_app.py -q`
  - `docker compose -p literature-screening-dev -f /Users/mao/Documents/langchain/docker-compose.dev.yml exec -T web npm run build`
  - `git diff --check literature_screening/src/literature_screening/api/schemas.py literature_screening/src/literature_screening/api/workspace_store.py literature_screening/src/literature_screening/api/app.py literature_screening/src/literature_screening/core/models.py literature_screening/src/literature_screening/bibtex/parser.py literature_screening/src/literature_screening/bibtex/deduper.py literature_screening/src/literature_screening/bibtex/exporter.py literature_screening/tests/test_api_app.py literature_screening_web/src/types/api.ts literature_screening_web/src/api/client.ts literature_screening_web/src/stores/projects.ts literature_screening_web/src/components/ScreeningRecordsTable.vue literature_screening_web/src/views/FulltextQueueView.vue literature_screening_web/src/views/ProjectDetailView.vue literature_screening_web/src/views/TaskDetailView.vue literature_screening_web/src/layouts/AppShell.vue literature_screening_web/src/views/DashboardView.vue`
- Outstanding follow-ups:
  - evaluate later whether uncertain papers should also be promoted into the merged full-text/final-review workspace instead of staying only in the screening detail layer
  - if imported RIS/EndNote metadata lacks a usable URL, discuss later whether title-based CNKI/Wanfang/VIP search is worth the complexity; for now, do not auto-scrape those sources
- Files touched:
  - `/Users/mao/Documents/langchain/literature_screening/src/literature_screening/api/schemas.py`
  - `/Users/mao/Documents/langchain/literature_screening/src/literature_screening/api/workspace_store.py`
  - `/Users/mao/Documents/langchain/literature_screening/src/literature_screening/api/app.py`
  - `/Users/mao/Documents/langchain/literature_screening/src/literature_screening/core/models.py`
  - `/Users/mao/Documents/langchain/literature_screening/src/literature_screening/bibtex/parser.py`
  - `/Users/mao/Documents/langchain/literature_screening/src/literature_screening/bibtex/deduper.py`
  - `/Users/mao/Documents/langchain/literature_screening/src/literature_screening/bibtex/exporter.py`
  - `/Users/mao/Documents/langchain/literature_screening/tests/test_api_app.py`
  - `/Users/mao/Documents/langchain/literature_screening_web/src/types/api.ts`
  - `/Users/mao/Documents/langchain/literature_screening_web/src/api/client.ts`
  - `/Users/mao/Documents/langchain/literature_screening_web/src/stores/projects.ts`
  - `/Users/mao/Documents/langchain/literature_screening_web/src/components/ScreeningRecordsTable.vue`
  - `/Users/mao/Documents/langchain/literature_screening_web/src/views/FulltextQueueView.vue`
  - `/Users/mao/Documents/langchain/literature_screening_web/src/views/ProjectDetailView.vue`
  - `/Users/mao/Documents/langchain/literature_screening_web/src/views/TaskDetailView.vue`
  - `/Users/mao/Documents/langchain/literature_screening_web/src/layouts/AppShell.vue`
  - `/Users/mao/Documents/langchain/literature_screening_web/src/views/DashboardView.vue`
  - `/Users/mao/Documents/langchain/project_state.md`
  - `/Users/mao/Documents/langchain/project_session_log.md`

## Session 2026-04-09 - Full-text review batching and include-only boundary cleanup

- Scope: made the merged full-text/final-review workspace feel closer to the original review flow by restoring bulk actions, switching its default order to year-first, and tightening the boundary so excluded/uncertain screening outcomes do not conceptually bleed into full-text work
- Main changes:
  - updated `/Users/mao/Documents/langchain/literature_screening_web/src/views/FulltextQueueView.vue` so the full-text page now defaults to year-desc ordering with relevance as the secondary sort inside each year, shows explicit selection checkboxes, and restores batch actions such as bulk exclude, bulk ready, bulk defer, and bulk unavailable
  - added `/Users/mao/Documents/langchain/literature_screening/src/literature_screening/api/schemas.py`, `/Users/mao/Documents/langchain/literature_screening/src/literature_screening/api/app.py`, `/Users/mao/Documents/langchain/literature_screening/src/literature_screening/api/workspace_store.py`, `/Users/mao/Documents/langchain/literature_screening_web/src/api/client.ts`, and `/Users/mao/Documents/langchain/literature_screening_web/src/stores/projects.ts` support for batch full-text status updates so the UI can update many selected papers with one rebuild instead of spamming single-item requests
  - tightened screening-context enrichment in `/Users/mao/Documents/langchain/literature_screening/src/literature_screening/api/app.py` so full-text queue context now matches by DOI / normalized title instead of unstable per-run `paper_id`, and later screening decisions of `exclude` / `uncertain` now remove matching items from the full-text queue instead of letting them linger there
  - added regression coverage in `/Users/mao/Documents/langchain/literature_screening/tests/test_api_app.py` for batch full-text status updates, for preventing excluded context from another screening round from leaking into the full-text queue via `paper_id` collision, and for filtering out papers whose latest matched screening decision is no longer `include`
- Verification:
  - `PYTHONPATH=/Users/mao/Documents/langchain/literature_screening/src ./.venv/bin/python -m pytest /Users/mao/Documents/langchain/literature_screening/tests/test_api_app.py -q`
  - `docker compose -p literature-screening-dev -f /Users/mao/Documents/langchain/docker-compose.dev.yml exec -T web npm run build`
  - `git diff --check literature_screening/src/literature_screening/api/app.py literature_screening/src/literature_screening/api/schemas.py literature_screening/src/literature_screening/api/workspace_store.py literature_screening/tests/test_api_app.py literature_screening_web/src/api/client.ts literature_screening_web/src/stores/projects.ts literature_screening_web/src/views/FulltextQueueView.vue`
- Outstanding follow-ups:
  - if future users want “不确定” records to enter a dedicated secondary queue, add that as an explicit optional source class instead of silently mixing it into the full-text queue
  - consider later whether the full-text page should visually group cards by year headers now that year-first sorting is the default
- Files touched:
  - `/Users/mao/Documents/langchain/literature_screening/src/literature_screening/api/app.py`
  - `/Users/mao/Documents/langchain/literature_screening/src/literature_screening/api/schemas.py`
  - `/Users/mao/Documents/langchain/literature_screening/src/literature_screening/api/workspace_store.py`
  - `/Users/mao/Documents/langchain/literature_screening/tests/test_api_app.py`
  - `/Users/mao/Documents/langchain/literature_screening_web/src/api/client.ts`
  - `/Users/mao/Documents/langchain/literature_screening_web/src/stores/projects.ts`
  - `/Users/mao/Documents/langchain/literature_screening_web/src/views/FulltextQueueView.vue`
  - `/Users/mao/Documents/langchain/project_state.md`
  - `/Users/mao/Documents/langchain/project_session_log.md`

## Session 2026-04-09 - Dashboard refresh and sidebar thread context menu

- Scope: cleaned up the homepage hierarchy so it reads more clearly, and made the sidebar recent-thread list support direct context actions instead of forcing users to hunt for edit/delete entry points
- Main changes:
  - redesigned `/Users/mao/Documents/langchain/literature_screening_web/src/views/DashboardView.vue` into a more balanced hero + overview + recent-thread layout, replacing the old sparse “如何使用” area with denser workflow guidance and reducing visual clutter on thread cards
  - changed recent thread cards on the dashboard to use a compact action dropdown instead of always showing separate edit/delete icon buttons
  - updated `/Users/mao/Documents/langchain/literature_screening_web/src/layouts/AppShell.vue` so sidebar recent-thread items are sorted by update time, highlight the active thread, and support right-click context actions for open, edit, and delete
  - added a lightweight global thread edit modal in `/Users/mao/Documents/langchain/literature_screening_web/src/layouts/AppShell.vue` so sidebar context-menu editing no longer requires bouncing through the homepage first
- Verification:
  - `docker compose -p literature-screening-dev -f /Users/mao/Documents/langchain/docker-compose.dev.yml exec -T web npm run build`
  - `git diff --check literature_screening_web/src/layouts/AppShell.vue literature_screening_web/src/views/DashboardView.vue`
- Outstanding follow-ups:
  - consider later whether the sidebar recent-thread list should also expose the same context menu on touch devices via a small visible “more” affordance
  - consider later whether the homepage recent-thread grid should support right-click context actions too, for parity with the sidebar
- Files touched:
  - `/Users/mao/Documents/langchain/literature_screening_web/src/layouts/AppShell.vue`
  - `/Users/mao/Documents/langchain/literature_screening_web/src/views/DashboardView.vue`
  - `/Users/mao/Documents/langchain/project_state.md`
  - `/Users/mao/Documents/langchain/project_session_log.md`

## Session 2026-04-09 - Unified screening and full-text review workspace

- Scope: merged the duplicated-feeling screening review and full-text acquisition interactions into a single review workspace while preserving each side's core controls
- Main changes:
  - rewrote `/Users/mao/Documents/langchain/literature_screening_web/src/views/FulltextQueueView.vue` into a unified “筛选与全文复核工作台” with two tabs on one route: `筛选复核` and `全文获取`
  - kept the screening-side powers inside the new screening tab, including selected-round review, single-record decision edits, multi-select batch review overrides, and title/reference-list matching
  - kept the full-text-side powers inside the full-text tab, including year-first queue ordering, OA/link refresh, selection-based batch status updates, per-item full-text notes, and final curation states
  - updated `/Users/mao/Documents/langchain/literature_screening_web/src/views/TaskDetailView.vue` so the screening task page now opens the unified workspace directly on the screening-review tab for the current screening round
  - updated `/Users/mao/Documents/langchain/literature_screening_web/src/views/ProjectDetailView.vue` so the thread homepage now consistently labels stage 3 as a unified review workspace instead of presenting screening follow-up and full-text acquisition as separate destinations
- Verification:
  - `docker compose -p literature-screening-dev -f /Users/mao/Documents/langchain/docker-compose.dev.yml exec -T web npm run build`
  - `git diff --check literature_screening_web/src/layouts/AppShell.vue literature_screening_web/src/views/DashboardView.vue literature_screening_web/src/views/FulltextQueueView.vue literature_screening_web/src/views/ProjectDetailView.vue literature_screening_web/src/views/TaskDetailView.vue`
- Outstanding follow-ups:
  - split `/Users/mao/Documents/langchain/literature_screening_web/src/views/FulltextQueueView.vue` into smaller subcomponents once the merged interaction settles down
  - consider adding a visible touch-friendly “more” button for sidebar thread actions so edit/delete remain discoverable without right click
- Files touched:
  - `/Users/mao/Documents/langchain/literature_screening_web/src/views/FulltextQueueView.vue`
  - `/Users/mao/Documents/langchain/literature_screening_web/src/views/TaskDetailView.vue`
  - `/Users/mao/Documents/langchain/literature_screening_web/src/views/ProjectDetailView.vue`
  - `/Users/mao/Documents/langchain/literature_screening_web/src/layouts/AppShell.vue`
  - `/Users/mao/Documents/langchain/literature_screening_web/src/views/DashboardView.vue`
  - `/Users/mao/Documents/langchain/project_state.md`
  - `/Users/mao/Documents/langchain/project_session_log.md`

## Session 2026-04-09 - Unified candidate stream redesign for review workspace

- Scope: refined the first merged review workspace so it no longer feels like two pages glued together, and removed the duplicated screening-record table from the screening task detail page
- Main changes:
  - rewrote `/Users/mao/Documents/langchain/literature_screening_web/src/views/FulltextQueueView.vue` again so the review area is now one continuous candidate stream with a right-side action panel instead of `筛选复核` / `全文获取` tabs
  - removed the old default-first-record behavior from the review workspace, so entering the page no longer auto-selects a paper before the user clicks or checks one
  - updated the unified candidate rows to show screening decision, confidence, and full-text stage together, while the right-side panel now switches between single-record handling, batch handling, and title/reference-list batch matching
  - updated `/Users/mao/Documents/langchain/literature_screening_web/src/views/TaskDetailView.vue` so screening task detail now focuses on round summary, thread criteria, outputs, and next actions instead of repeating the review table and advanced-fix forms
  - simplified the screening-task jump into the review workspace so it now only passes `screeningTaskId` instead of a tab-specific route intent
- Verification:
  - `docker compose -p literature-screening-dev -f /Users/mao/Documents/langchain/docker-compose.dev.yml exec -T web npm run build`
  - `git diff --check literature_screening_web/src/views/FulltextQueueView.vue literature_screening_web/src/views/TaskDetailView.vue project_state.md project_session_log.md`
- Outstanding follow-ups:
  - split `/Users/mao/Documents/langchain/literature_screening_web/src/views/FulltextQueueView.vue` into smaller subcomponents once the new candidate-stream interaction settles down
  - consider later whether the unified candidate stream should add optional year headers once larger real-world projects make the year-first order feel dense
- Files touched:
  - `/Users/mao/Documents/langchain/literature_screening_web/src/views/FulltextQueueView.vue`
  - `/Users/mao/Documents/langchain/literature_screening_web/src/views/TaskDetailView.vue`
  - `/Users/mao/Documents/langchain/project_state.md`
  - `/Users/mao/Documents/langchain/project_session_log.md`

## Session 2026-04-10 - Strategy localization and thread auto-rename

- Scope: fixed the new-thread kickoff flow so generated strategy output becomes the thread’s visible identity, and localized strategy output by database so the resulting topic, summary, criteria, and search syntax match the expected Chinese/English split
- Main changes:
  - updated `/Users/mao/Documents/langchain/literature_screening_web/src/views/StrategyRunView.vue` and `/Users/mao/Documents/langchain/literature_screening_web/src/stores/drafts.ts` so opening “新建线程” no longer auto-fills the last saved draft; the page now stays blank and only restores old content when the user explicitly chooses to do so
  - updated `/Users/mao/Documents/langchain/literature_screening/src/literature_screening/strategy/prompt_builder.py` so `topic`, `intent_summary`, `screening_topic`, inclusion/exclusion criteria, notes, and CNKI rows are required in Chinese, while Scopus / WoS / PubMed search expressions are required in English
  - updated `/Users/mao/Documents/langchain/literature_screening/src/literature_screening/api/app.py` so a completed strategy task now renames the thread to the generated `topic`, updates the thread description to the generated Chinese `intent_summary`, and keeps the generated Chinese `screening_topic` as the screening default
  - added regression coverage in `/Users/mao/Documents/langchain/literature_screening/tests/test_strategy_module.py` and `/Users/mao/Documents/langchain/literature_screening/tests/test_api_app.py` for the new language contract and for post-strategy thread rename / description persistence
- Verification:
  - `PYTHONPATH=/Users/mao/Documents/langchain/literature_screening/src ./.venv/bin/python -m pytest /Users/mao/Documents/langchain/literature_screening/tests/test_strategy_module.py /Users/mao/Documents/langchain/literature_screening/tests/test_api_app.py -q`
  - `git diff --check /Users/mao/Documents/langchain/literature_screening/src/literature_screening/strategy/prompt_builder.py /Users/mao/Documents/langchain/literature_screening/src/literature_screening/api/app.py /Users/mao/Documents/langchain/literature_screening/tests/test_strategy_module.py /Users/mao/Documents/langchain/literature_screening/tests/test_api_app.py`
- Outstanding follow-ups:
  - older threads that already generated a strategy before this update still need one manual “重新生成线程方案” run if the user wants their visible name, summary, and criteria refreshed into the new localized format
  - if later users want database titles themselves localized differently by provider, refine the renderer and thread summary cards without changing the core prompt contract again
- Files touched:
  - `/Users/mao/Documents/langchain/literature_screening_web/src/views/StrategyRunView.vue`
  - `/Users/mao/Documents/langchain/literature_screening_web/src/stores/drafts.ts`
  - `/Users/mao/Documents/langchain/literature_screening/src/literature_screening/strategy/prompt_builder.py`
  - `/Users/mao/Documents/langchain/literature_screening/src/literature_screening/api/app.py`
  - `/Users/mao/Documents/langchain/literature_screening/tests/test_strategy_module.py`
  - `/Users/mao/Documents/langchain/literature_screening/tests/test_api_app.py`
  - `/Users/mao/Documents/langchain/project_state.md`
  - `/Users/mao/Documents/langchain/project_session_log.md`

## Session 2026-04-11 - Rename active branch to thread-first workflow refresh

- Scope: renamed the long-lived working branch so its name matches the current product scope instead of the older relative-path-only backend fix
- Main changes:
  - renamed the local git branch from `codex/relative-path-api-compat` to `codex/thread-first-workflow-refresh`
  - pushed the renamed branch to GitHub and removed the old remote branch name to keep the remote clean
  - updated `/Users/mao/Documents/langchain/project_state.md` so current-branch and remote-tracking references now point at the renamed branch
- Verification:
  - `git branch --show-current`
  - `git push -u origin codex/thread-first-workflow-refresh`
  - `git push origin --delete codex/relative-path-api-compat`
- Outstanding follow-ups:
  - if a later PR is opened from this work, use `codex/thread-first-workflow-refresh` as the head branch name
- Files touched:
  - `/Users/mao/Documents/langchain/project_state.md`
  - `/Users/mao/Documents/langchain/project_session_log.md`

## Session 2026-04-11 - Survey/Tutorial review-writing baseline scaffolding

- Scope: created a local baseline (sources + rubric + templates + prompts) for turning screened literature into a Survey/Tutorial-style review draft, with cross-platform artifact contracts.
- Main changes:
  - added `review_writing_baseline/` with:
    - `sources/manifest.yaml` and distilled notes under `sources/notes/`
    - artifact contract + portability conventions under `specs/`
    - measurable rubric + table schemas + outline template under `baseline/`
    - prompt building blocks under `prompts/`
    - small tooling scripts under `tools/` (`scaffold_project.py`, `rubric_check.py`)
  - added `review_writing_baseline/project_template/` for a stable on-disk project layout
  - added `.gitignore` patterns for heavy `review_projects/**` artifacts (PDFs/exports/cache)
  - created a repo-specific Codex handoff skill at `C:\\Users\\heiba\\.codex\\skills\\review-project-state\\SKILL.md`
  - updated `project_state.md` to reflect this baseline and the current workspace root
- Verification:
  - `python review_writing_baseline/tools/scaffold_project.py demo_survey --dest-root tmp_review_projects`
  - `python review_writing_baseline/tools/rubric_check.py tmp_review_projects/demo_survey`
- Outstanding follow-ups:
  - wire the baseline prompts/contracts into the existing backend pipeline (so a thread can export `papers_canonical.csv`, decisions, taxonomy, and draft stubs automatically)
  - add an optional “venue profile” layer (COMST/ProcIEEE/CSUR-style) that tweaks rubric thresholds and required artifacts
  - decide whether to keep `review_projects/` ignored by default or add a small example project fixture for demos/tests
- Files touched:
  - `E:\\aixiaowo\\review\\review_writing_baseline\\README.md`
  - `E:\\aixiaowo\\review\\review_writing_baseline\\sources\\manifest.yaml`
  - `E:\\aixiaowo\\review\\review_writing_baseline\\baseline\\rubric_survey.yaml`
  - `E:\\aixiaowo\\review\\review_writing_baseline\\tools\\rubric_check.py`
  - `E:\\aixiaowo\\review\\review_writing_baseline\\tools\\scaffold_project.py`
  - `E:\\aixiaowo\\review\\project_state.md`
  - `E:\\aixiaowo\\review\\project_session_log.md`

## Session 2026-04-11 - Survey baseline integration bridge + system design note

- Scope: made the survey baseline more runnable out of the box and documented how it maps onto the existing screening/strategy modules.
- Main changes:
  - added `review_writing_baseline/specs/system_design_survey.md` describing phased implementation and what to reuse from `literature_screening`
  - added `review_writing_baseline/tools/import_from_screening_output.py` to convert a screening run output dir into `papers_canonical.csv` + `abstract_decisions.csv`
  - updated the project template to include a header-only `02_import/papers_canonical.csv` so rubric blockers pass immediately after scaffolding
- Verification:
  - `python review_writing_baseline/tools/scaffold_project.py demo_survey --dest-root tmp_review_projects`
  - `python review_writing_baseline/tools/rubric_check.py tmp_review_projects/demo_survey`
- Outstanding follow-ups:
  - implement the Phase 2 taxonomy/table planning step as a detached module (similar to `formal_report_module`) so it can run on included abstracts
  - decide whether review-writing should become a new `TaskKind` (`review`) in the API/UI or remain “file-first” CLI-driven for a while
- Files touched:
  - `E:\\aixiaowo\\review\\review_writing_baseline\\specs\\system_design_survey.md`
  - `E:\\aixiaowo\\review\\review_writing_baseline\\tools\\import_from_screening_output.py`
  - `E:\\aixiaowo\\review\\review_writing_baseline\\project_template\\02_import\\papers_canonical.csv`
  - `E:\\aixiaowo\\review\\project_state.md`
  - `E:\\aixiaowo\\review\\project_session_log.md`

## Session 2026-04-11 - Separate Wenxian app vs review agent baseline

- Scope: reorganized `E:\\aixiaowo\\review` to separate the existing screening system from the new Survey/Tutorial review-writing baseline.
- Main changes:
  - moved the existing Wenxian app into `E:\\aixiaowo\\review\\wenxian\\` (backend, web, compose files, scripts, deploy docs)
  - moved the review-writing baseline into `E:\\aixiaowo\\review\\review_agent\\review_writing_baseline\\`
  - updated root `.gitignore` to match the new folder layout
  - updated baseline docs/prompts so referenced paths match the new location
- Verification:
  - `python review_agent/review_writing_baseline/tools/scaffold_project.py demo_survey --dest-root tmp_review_projects`
  - `python review_agent/review_writing_baseline/tools/rubric_check.py tmp_review_projects/demo_survey`
- Outstanding follow-ups:
  - update any external tools/skills that hardcode `E:\\aixiaowo\\review\\project_state.md` paths if they should now point to the new layout
- Files touched:
  - `E:\\aixiaowo\\review\\.gitignore`
  - `E:\\aixiaowo\\review\\project_state.md`
  - `E:\\aixiaowo\\review\\project_session_log.md`
  - `E:\\aixiaowo\\review\\review_agent\\review_writing_baseline\\specs\\artifact_contract_survey.md`
  - `E:\\aixiaowo\\review\\review_agent\\review_writing_baseline\\specs\\system_design_survey.md`
  - `E:\\aixiaowo\\review\\review_agent\\review_writing_baseline\\sources\\manifest.yaml`

## Session 2026-04-11 - Make Stage 04/05 stronger (taxonomy mapping + fulltext priority + table plan)

- Scope: improved the artifact-driven survey workflow so it can produce better outlines and guide full-text collection more effectively.
- Main changes:
  - expanded the survey artifact contract to include optional but high-value planning artifacts:
    - `03_screening/screening_summary.json`
    - `04_taxonomy/paper_classification.csv`
    - `04_taxonomy/fulltext_priority.csv`
    - `04_taxonomy/table_figure_plan.yaml`
    - `06_draft/claims_map.csv`
  - extended the survey rubric with warn-level checks for those artifacts
  - added `review_agent/review_writing_baseline/specs/stage_playbook_survey.md` and `review_agent/review_writing_baseline/specs/screening_reason_tags.yaml`
  - added table schemas: `decision_matrix.yaml` and `taxonomy_overview.yaml`
  - updated the project template with placeholders for the new artifacts
- Verification:
  - `python review_agent/review_writing_baseline/tools/scaffold_project.py demo_survey --dest-root tmp_review_projects`
  - `python review_agent/review_writing_baseline/tools/rubric_check.py tmp_review_projects/demo_survey`
- Outstanding follow-ups:
  - implement tooling to auto-generate `paper_classification.csv`, `fulltext_priority.csv`, and `table_figure_plan.yaml` from included abstracts (human-in-the-loop edits)
- Files touched:
  - `E:\\aixiaowo\\review\\review_agent\\review_writing_baseline\\specs\\artifact_contract_survey.md`
  - `E:\\aixiaowo\\review\\review_agent\\review_writing_baseline\\specs\\stage_playbook_survey.md`
  - `E:\\aixiaowo\\review\\review_agent\\review_writing_baseline\\baseline\\rubric_survey.yaml`

## Session 2026-04-11 - Project plan doc + handoff refresh for new thread

- Scope: wrote a concrete end-to-end plan for the Survey/Tutorial review agent and refreshed handoff docs so a new thread can start implementation immediately.
- Main changes:
  - added `E:\\aixiaowo\\review\\review_agent\\PROJECT_PLAN.md` (phases, artifacts, success criteria)
  - updated `E:\\aixiaowo\\review\\project_state.md` to highlight the review-agent next steps and list primary paths for this workspace (while keeping older notes as legacy)
- Verification:
  - `python review_agent/review_writing_baseline/tools/rubric_check.py` (used previously to validate scaffolding; no new execution-specific checks added here)
- Outstanding follow-ups:
  - start Phase 1 implementation: abstracts → taxonomy + mapping + fulltext priority + table/figure plan
- Files touched:
  - `E:\\aixiaowo\\review\\review_agent\\PROJECT_PLAN.md`
  - `E:\\aixiaowo\\review\\project_state.md`
  - `E:\\aixiaowo\\review\\project_session_log.md`

## Session 2026-04-11 - Review Web MVP (Vue + FastAPI) + Phase 1 tool

- Scope: implemented a runnable UI + API for the artifact-driven review-writing workflow, plus Phase 1 (abstracts -> taxonomy + planning artifacts) so the system is immediately usable.
- Main changes:
  - added Phase 1 generator: `review_agent/review_writing_baseline/tools/phase1_abstract_to_taxonomy.py`
  - added Review Web backend (FastAPI): `review_agent/review_web/backend/`
  - added Review Web frontend (Vue + Vite) and built `dist/` so backend can serve it: `review_agent/review_web/frontend/`
  - scaffolded a demo project with sample metadata and generated Phase 1 outputs: `review_agent/review_projects/demo_survey_web/`
  - added Windows one-command launcher: `start-review-web.ps1` (default port: `8731`)
- Verification:
  - `python -m py_compile review_agent/review_writing_baseline/tools/phase1_abstract_to_taxonomy.py`
  - `python review_agent/review_writing_baseline/tools/phase1_abstract_to_taxonomy.py review_agent/review_projects/demo_survey_web`
  - `python review_agent/review_writing_baseline/tools/rubric_check.py review_agent/review_projects/demo_survey_web`
  - started uvicorn and verified:
    - `GET http://127.0.0.1:8731/api/projects`
    - `GET http://127.0.0.1:8731/`
- Outstanding follow-ups:
  - add a better Phase 1 taxonomy/clustering strategy (human-in-the-loop edits + stability across reruns)
  - add Phase 2 PDF ingestion and paper-card extraction pipeline (`05_evidence/paper_cards/*.json`)
  - improve the UI with markdown preview + taxonomy tree visualization
- Files touched:
  - `E:\\aixiaowo\\review\\review_agent\\review_writing_baseline\\tools\\phase1_abstract_to_taxonomy.py`
  - `E:\\aixiaowo\\review\\review_agent\\review_web\\backend\\app\\api.py`
  - `E:\\aixiaowo\\review\\review_agent\\review_web\\backend\\app\\main.py`
  - `E:\\aixiaowo\\review\\review_agent\\review_web\\backend\\app\\paths.py`
  - `E:\\aixiaowo\\review\\review_agent\\review_web\\backend\\app\\tools.py`
  - `E:\\aixiaowo\\review\\review_agent\\review_web\\backend\\requirements.txt`
  - `E:\\aixiaowo\\review\\review_agent\\review_web\\backend\\run.ps1`
  - `E:\\aixiaowo\\review\\review_agent\\review_web\\frontend\\src\\App.vue`
  - `E:\\aixiaowo\\review\\review_agent\\review_web\\frontend\\src\\api.ts`
  - `E:\\aixiaowo\\review\\review_agent\\review_web\\README.md`
  - `E:\\aixiaowo\\review\\start-review-web.ps1`
  - `E:\\aixiaowo\\review\\review_agent\\review_projects\\demo_survey_web\\02_import\\papers_canonical.csv`
  - `E:\\aixiaowo\\review\\review_agent\\review_projects\\demo_survey_web\\03_screening\\abstract_decisions.csv`
  - `E:\\aixiaowo\\review\\project_state.md`
  - `E:\\aixiaowo\\review\\project_session_log.md`

## Session 2026-04-11 - Review Web UX pass (guided Workbench)

- Scope: improved end-user usability so a new user can follow a linear flow without understanding artifact files first.
- Main changes:
  - added `GET /api/projects/{slug}/stats` for artifact/counter hints
  - redesigned frontend default view into a guided “工作台”:
    - editable tables for `papers_canonical.csv` and `abstract_decisions.csv`
    - Phase 1 gated by include count and quick previews for taxonomy/outline
    - kept “文件” mode for advanced direct editing
  - fixed previous garbled UI strings by rewriting the frontend UI copy
- Verification:
  - started uvicorn and verified `/` and `/api/projects/demo_survey_web/stats` respond (port `8731`)
  - `npm run build` for the frontend bundle
- Outstanding follow-ups:
  - add markdown preview + taxonomy tree visualization in Workbench
  - Phase 2 PDF ingestion and paper-card extraction UI
- Files touched:
  - `E:\\aixiaowo\\review\\review_agent\\review_web\\backend\\app\\api.py`
  - `E:\\aixiaowo\\review\\review_agent\\review_web\\frontend\\src\\App.vue`
  - `E:\\aixiaowo\\review\\review_agent\\review_web\\frontend\\src\\styles.css`
  - `E:\\aixiaowo\\review\\review_agent\\review_web\\frontend\\package.json`
  - `E:\\aixiaowo\\review\\project_state.md`
  - `E:\\aixiaowo\\review\\project_session_log.md`

## Session 2026-04-11 - Phases 2–4 + responsive Workbench

- Scope: completed a minimal end-to-end Survey/Tutorial pipeline in Review Web (Phase 1–4) and fixed the layout so the UI is usable on normal screens.
- Main changes:
  - Phase 2: PDF upload + extraction -> `05_evidence/paper_cards/*.json` and `05_evidence/chunks/chunks.jsonl`
  - Phase 3: tables-first drafting scaffolds/refreshes key draft section files under `06_draft/`
  - Phase 4: traceability check generates `06_draft/claims_map.csv` and `07_quality/traceability_report.md`
  - UI: added Workbench sections for PDF upload and Phase 2/3/4 outputs, and made panels scrollable/responsive
- Verification:
  - started uvicorn and verified OpenAPI exposes `pdfs` + `phase2/3/4` endpoints on `8731`
  - uploaded a test PDF via `curl.exe -F` and ran Phase 2/3/4 successfully for `demo_survey_web`
  - `npm run build` for the updated frontend bundle
- Files touched:
  - `E:\\aixiaowo\\review\\review_agent\\review_web\\backend\\app\\api.py`
  - `E:\\aixiaowo\\review\\review_agent\\review_web\\backend\\requirements.txt`
  - `E:\\aixiaowo\\review\\review_agent\\review_web\\backend\\run.ps1`
  - `E:\\aixiaowo\\review\\review_agent\\review_web\\frontend\\src\\App.vue`
  - `E:\\aixiaowo\\review\\review_agent\\review_web\\frontend\\src\\api.ts`
  - `E:\\aixiaowo\\review\\review_agent\\review_web\\frontend\\src\\styles.css`
  - `E:\\aixiaowo\\review\\review_agent\\review_writing_baseline\\tools\\phase2_pdf_to_paper_cards.py`
  - `E:\\aixiaowo\\review\\review_agent\\review_writing_baseline\\tools\\phase3_tables_first_draft.py`
  - `E:\\aixiaowo\\review\\review_agent\\review_writing_baseline\\tools\\phase4_traceability_check.py`
  - `E:\\aixiaowo\\review\\project_state.md`
  - `E:\\aixiaowo\\review\\project_session_log.md`
