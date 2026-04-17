# Workspace: Wenxian + Review Agent

This workspace intentionally contains **two separated systems**:

## 1) `wenxian/` — literature screening system

Purpose: generate search plans, batch-screen abstracts, manage full-text queue, and produce post-screening reports.

Key entry points:

- Backend: `wenxian/literature_screening/`
- Frontend: `wenxian/literature_screening_web/`
- Compose:
  - stable: `wenxian/docker-compose.local.yml`
  - dev: `wenxian/docker-compose.dev.yml`
- Start/stop scripts:
  - `wenxian/start-wenxian.command`
  - `wenxian/start-wenxian-dev.command`
  - `wenxian/stop-wenxian.command`
  - `wenxian/stop-wenxian-dev.command`

## 2) `review_agent/` — Survey/Tutorial review-writing system (in progress)

Purpose: turn screened literature into a **computer-science Survey/Tutorial** with measurable quality gates (rubric), stable artifacts, and reusable prompts/templates.

Key entry points:

- Baseline: `review_agent/review_writing_baseline/`
- Specs:
  - artifact contract: `review_agent/review_writing_baseline/specs/artifact_contract_survey.md`
  - system design: `review_agent/review_writing_baseline/specs/system_design_survey.md`
  - conventions: `review_agent/review_writing_baseline/specs/repo_conventions.md`
- Rubric + tooling:
  - rubric: `review_agent/review_writing_baseline/baseline/rubric_survey.yaml`
  - scaffold: `review_agent/review_writing_baseline/tools/scaffold_project.py`
  - check: `review_agent/review_writing_baseline/tools/rubric_check.py`

Recommended working data folder (gitignored by default):

- `review_agent/review_projects/<project_slug>/`

## Project state / handoff

- `project_state.md`
- `project_session_log.md`

