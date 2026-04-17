# Review Agent Project Plan (Survey/Tutorial, artifact-driven)

This document turns the “idea” into an executable plan: what we build, what files it reads/writes, and what “done” means.

## Goal

Build an agentic workflow that helps a human produce a **computer-science Survey/Tutorial**:

- fast first outline + taxonomy from abstracts
- evidence-driven tables/figures planning
- full-text prioritization (which PDFs to fetch next, and why)
- full-text extraction into reusable “paper cards”
- draft sections + tables that are measurable by a rubric

## Non-goals (for now)

- fully automated “one-click publishable survey”
- SLR/PRISMA-first workflow (can be added later as a separate mode)
- tightly coupled UI changes inside `wenxian/` (we start file-first)

## Design principle: artifacts coordinate everything

We do **not** rely on multi-agent “chat memory” to coordinate.

Instead, every step reads and writes stable artifacts under:

- `review_agent/review_projects/<project_slug>/`

Contract and playbook:

- `review_agent/review_writing_baseline/specs/artifact_contract_survey.md`
- `review_agent/review_writing_baseline/specs/stage_playbook_survey.md`

Quality gate:

- `review_agent/review_writing_baseline/baseline/rubric_survey.yaml`
- checker: `review_agent/review_writing_baseline/tools/rubric_check.py`

## Workflow (high-level)

1. Stage 00–02: frame topic, generate search syntax, import & canonicalize metadata
2. Stage 03: abstract triage (include/exclude/uncertain)
3. Stage 04: taxonomy + mapping + “table/figure plan” + full-text priority list
4. Stage 05: user fetches PDFs for prioritized papers; system extracts paper cards (+ later: RAG evidence pointers)
5. Stage 06: draft outline → chapters → tables; iterate with rubric gates
6. Stage 07: traceability check (claims/tables must link to evidence pointers)

## Core artifacts (what makes the workflow strong)

Minimum “blocking” artifacts (rubric blockers):

- `00_project.yaml`
- `01_search_terms.yaml`
- `02_import/papers_canonical.csv`
- `03_screening/abstract_decisions.csv`
- `04_taxonomy/taxonomy.yaml`
- `06_draft/00_outline.md`

High-value planning artifacts (rubric warns; should exist before serious drafting):

- `04_taxonomy/paper_classification.csv` (paper_id → taxonomy node + confidence)
- `04_taxonomy/table_figure_plan.yaml` (planned tables/figures + required evidence fields)
- `04_taxonomy/fulltext_priority.csv` (which PDFs to fetch next + extraction needs)

Evidence & writing artifacts:

- `05_evidence/paper_cards/<paper_id>.json`
- `05_evidence/extracted_tables/*` (rows that match schemas in `review_agent/review_writing_baseline/baseline/table_schemas/`)
- `06_draft/*.md`

## Phased implementation plan

### Phase 1 — “Abstract-to-Taxonomy + Fulltext Priority” (highest ROI)

Deliver:

- a tool/task that reads included abstracts and writes:
  - `taxonomy.yaml` (v0.1, abstract-based)
  - `paper_classification.csv`
  - `table_figure_plan.yaml`
  - `fulltext_priority.csv`

Why:

- this is the missing “planning layer” between screening and full-text work
- it turns a pile of abstracts into a structured next-action list

### Phase 2 — Full-text extraction into paper cards (representative papers)

Deliver:

- a tool/task that takes `fulltext_priority.csv` + PDFs and writes `paper_cards/*.json`
- extraction fields must support comparison tables (datasets/metrics/assumptions/compute/reproducibility/failure modes)

### Phase 3 — Tables-first drafting

Deliver:

- generate stable tables (method comparison, dataset benchmark, decision matrix) before long narrative drafting
- generate `06_draft/00_outline.md` that references planned tables/figures per section

### Phase 4 — Evidence pointers (RAG) + traceability

Deliver:

- chunk PDFs into `05_evidence/chunks/chunks.jsonl` (page pointers)
- vector index (gitignored) for retrieval
- `claims_map.csv` / `traceability_report.md` to list missing evidence for draft claims and table cells

## Integration with `wenxian/`

`wenxian/` remains the screening system (strategy + abstract screening + full-text queue).

We integrate via file artifacts:

- convert a Wenxian screening output dir into review-project artifacts using:
  - `review_agent/review_writing_baseline/tools/import_from_screening_output.py`

Later (optional):

- add a new “review-writing” stage in the Wenxian UI that runs Phase 1 and exports artifacts.

## Success criteria (measurable)

- A new topic can reach a useful outline + taxonomy in < 1 hour from abstracts-only input.
- For each taxonomy leaf, the system outputs a ranked full-text list with explicit extraction needs.
- Tables/figures plan exists and is stable across iterations (only refined, not reinvented).
- Rubric blockers pass automatically; warnings shrink over time as evidence is added.

## Conventions

- All stored paths are workspace-relative (see `review_agent/review_writing_baseline/specs/repo_conventions.md`).
- Avoid mixing SLR requirements into Survey/Tutorial mode; add a separate mode later.

