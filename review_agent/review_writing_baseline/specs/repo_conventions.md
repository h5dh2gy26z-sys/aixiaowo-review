# Repo Conventions (cross-platform)

These conventions exist so review projects can move across macOS / Linux / Windows without path breakage.

## Paths

- Store paths in configs/artifacts as **workspace-relative** paths.
- Prefer forward slashes in stored strings (e.g. `review_agent/review_projects/demo_survey/02_import/papers_canonical.csv`), and resolve with `pathlib` when executing.
- If an absolute path is unavoidable (e.g. a user-selected local library folder), store it under a clearly named field like `local_absolute_path` and keep a sibling `relative_path` when possible.

## Data directories

- Keep “runs” and user-imported exports under `review_agent/review_projects/<project_slug>/`.
- Do not commit large exports or PDFs by default (see `.gitignore` guidance); commit only small fixtures.

## Text files

- Use UTF-8.
- Use LF line endings in new Markdown/YAML/JSON files.

## Naming

- `snake_case` for YAML keys.
- Artifact filenames start with a 2-digit stage prefix (`00_...`, `01_...`) to keep the pipeline order stable.
