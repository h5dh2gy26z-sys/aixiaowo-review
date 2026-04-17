# Survey/Tutorial Review System Design (how to reuse existing Wenxian modules)

Goal: turn a fuzzy research direction into a **Survey/Tutorial** draft with measurable quality gates (rubric) and stable intermediate artifacts.

This design intentionally starts **file-first** (artifact-driven) and can later be wired into the existing thread-first UI.

## Key idea: artifacts are the coordination layer

Instead of coordinating many agents by “chat memory”, coordinate by writing/reading stable files under:

- `review_agent/review_projects/<project_slug>/...` (see `review_agent/review_writing_baseline/specs/artifact_contract_survey.md`)

The rubric (`review_agent/review_writing_baseline/baseline/rubric_survey.yaml`) is the “definition of done”.

## What to reuse from the current repo

Already available capabilities we can reuse directly:

1. Strategy (search plan) generation
   - `wenxian/literature_screening/src/literature_screening/strategy/*`
   - Output already includes: topic name, intent summary, inclusion/exclusion criteria, and DB-specific query strings.
2. Screening pipeline (abstract triage)
   - `wenxian/literature_screening/src/literature_screening/pipeline/run_pipeline.py`
   - Outputs include `deduped_records.json` + `screening_decisions.json` + `included.ris`/`excluded.ris`.
3. Full-text queue & persistence
   - API + UI already support moving included papers through full-text states (`pending/ready/...`).
4. LLM client and retry/backoff utilities
   - `wenxian/literature_screening/src/literature_screening/screening/llm_client.py`
5. Detached module pattern for post-screening generation
   - `wenxian/literature_screening/separated_modules/formal_report_module` shows how to read screening outputs and generate new artifacts.

## Proposed workflow (phased)

### Phase 1 (MVP): scaffold review project from screening outputs

Inputs:

- Strategy output (topic + inclusion/exclusion + DB queries)
- Screening output dir (from `run_pipeline`) containing:
  - `deduped_records.json`
  - `screening_decisions.json`
  - `config.snapshot.json` (optional but useful)

Outputs (review project artifacts):

- `00_project.yaml` (scope + audience + constraints)
- `01_search_terms.yaml` (queries)
- `02_import/papers_canonical.csv` (normalized metadata/abstracts)
- `03_screening/abstract_decisions.csv` (include/exclude/uncertain + reason tags)
- `04_taxonomy/taxonomy.yaml` (placeholder or initial taxonomy)
- `06_draft/00_outline.md` (outline stub)
- `07_quality/rubric_report.md` (rubric results)

Implementation approach:

- Add a small importer script that converts a screening run output dir into a review project folder.

### Phase 2: taxonomy + table planning from abstracts

Inputs:

- included papers list + abstracts

Outputs:

- `taxonomy.yaml` refined with node definitions + inclusion rules
- one or more structured tables under `05_evidence/extracted_tables/` using schemas in `review_agent/review_writing_baseline/baseline/table_schemas/`

Implementation approach:

- Use LLM to propose taxonomy; enforce “no overlap between siblings” and “every paper must map”.
- Keep taxonomy editable by human; agent only proposes diffs.

### Phase 3: full-text extraction → paper cards

Inputs:

- PDFs for key papers (from the existing full-text queue)

Outputs:

- `05_evidence/paper_cards/<paper_id>.json`

Implementation approach:

- Implement a PDF→text step (local tool) then LLM extraction into a stable JSON schema.

### Phase 4: draft generation and rubric gates

Inputs:

- taxonomy + paper cards + extracted tables

Outputs:

- `06_draft/*.md` sections and tables
- `07_quality/rubric_report.md` must pass all blockers

Implementation approach:

- Generate section-by-section, with mandatory “takeaways”.
- Separate “style pass” (IEEE style) from “content pass”.

## UI wiring (later)

Once Phase 1–2 are stable, wire into the existing thread UI as a new stage after screening/full-text:

- add a new task kind like `review` (or multiple: `taxonomy`, `outline`, `draft`, `tables`)
- store generated artifacts as datasets/artifacts attached to the thread
- provide “export to `review_agent/review_projects/<slug>`” for power users
