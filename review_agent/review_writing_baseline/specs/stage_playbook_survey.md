# Stage Playbook (Survey/Tutorial, artifact-driven)

This document makes the “artifact-driven” coordination concrete: each stage has a fixed **input set**, produces a fixed **output artifact**, and can be rerun safely.

Canonical contract reference:

- `review_agent/review_writing_baseline/specs/artifact_contract_survey.md`
- Rubric gate: `review_agent/review_writing_baseline/baseline/rubric_survey.yaml`

## Project root

One review project lives at:

- `review_agent/review_projects/<project_slug>/`

## Stage 00 — Project framing

Goal: lock scope so later stages cannot drift.

Inputs:

- human-written intent

Outputs:

- `00_project.yaml`

Invariants:

- `scope_in` + `scope_out` must be explicit and non-empty.
- `audience` must be explicit (who you are teaching / convincing).

## Stage 01 — Search terms / queries

Goal: generate editable search queries (not “final truth”).

Inputs:

- `00_project.yaml`

Outputs:

- `01_search_terms.yaml` (per database: Scopus/WoS/PubMed/CNKI)

Invariants:

- queries reflect `scope_out` (explicit exclusions where needed)
- English queries for Scopus/WoS/PubMed; CNKI can be Chinese concept-lines

## Stage 02 — Import & canonicalization

Goal: normalize metadata into one table with stable `paper_id`.

Inputs (one of):

- your exports (`.csv/.ris/.enw/.bib/...`) placed under `02_import/`
- OR Wenxian screening output dir (`deduped_records.json` etc.)

Outputs:

- `02_import/papers_canonical.csv`

Invariants:

- required columns exist: `paper_id,title,year,abstract,doi`
- `paper_id` is stable and unique within the project

Notes:

- If you already ran Wenxian screening, use:
  - `review_agent/review_writing_baseline/tools/import_from_screening_output.py`

## Stage 03 — Abstract triage (include/exclude/uncertain)

Goal: build a first-pass corpus to support taxonomy and drafting.

Inputs:

- `00_project.yaml`
- `02_import/papers_canonical.csv`

Outputs:

- `03_screening/abstract_decisions.csv`
- `03_screening/screening_summary.json` (optional)

Invariants:

- decision is one of: `include|exclude|uncertain`
- `reason_tag` uses the controlled list in `review_agent/review_writing_baseline/specs/screening_reason_tags.yaml`

## Stage 04 — Taxonomy (the backbone of a CS survey)

Goal: define “how the field is organized” so the paper is not a list of works.

Inputs:

- included (and optionally uncertain) set from Stage 03

Outputs:

- `04_taxonomy/taxonomy.yaml`
- `04_taxonomy/paper_classification.csv` (optional)
- `04_taxonomy/fulltext_priority.csv` (optional)
- `04_taxonomy/table_figure_plan.yaml` (optional)

Invariants:

- sibling categories have minimal overlap
- every included paper can be mapped to at least one leaf node

## Stage 05 — Evidence extraction (full text → paper cards)

Goal: make evidence reusable across tables + chapters with traceable pointers.

Inputs:

- PDFs for selected key papers

Outputs:

- `05_evidence/paper_cards/<paper_id>.json`
- `05_evidence/chunks/chunks.jsonl` (optional once RAG is enabled)

Invariants:

- every strong claim includes evidence pointers (at minimum: page/chunk ids once RAG is enabled)
- unknown fields are `null` (no guessing)

## Stage 06 — Writing & tables

Goal: generate a structured survey draft that is “taxonomy + comparison + insight”.

Inputs:

- `04_taxonomy/taxonomy.yaml`
- `05_evidence/paper_cards/*.json` (for key works)
- table schemas under `review_agent/review_writing_baseline/baseline/table_schemas/`

Outputs:

- `06_draft/00_outline.md` (first)
- then `06_draft/*.md` sections
- `05_evidence/extracted_tables/*` (table rows)

Invariants:

- each major section ends with “takeaways”
- comparison tables use stable schemas (so they can be regenerated)

## Stage 07 — Rubric gate (quality check)

Goal: make progress measurable and prevent “draft drift”.

Inputs:

- the project directory

Outputs:

- command output (and optionally `07_quality/rubric_report.md`)

Command:

```bash
python review_agent/review_writing_baseline/tools/rubric_check.py review_agent/review_projects/<project_slug>
```
