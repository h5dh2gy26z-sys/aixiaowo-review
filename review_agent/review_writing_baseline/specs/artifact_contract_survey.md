# Artifact Contract (Survey/Tutorial)

This contract defines stable “inputs/outputs” between agent stages. Each stage reads files from prior stages and writes new artifacts.

## Directory layout (recommended)

```
review_agent/review_projects/<project_slug>/
  00_project.yaml
  01_search_terms.yaml
  02_import/
    papers_raw.*            # user exported CSV/RIS/ENW/BIB etc (optional)
    papers_canonical.csv    # normalized schema (recommended)
  03_screening/
    abstract_decisions.csv
    screening_summary.json  # optional: counts, missing fields, year/venue histogram
  04_taxonomy/
    taxonomy.yaml
    paper_classification.csv   # optional: paper_id -> taxonomy node(s) + confidence
    fulltext_priority.csv      # optional: prioritized full-text list with reasons + extraction needs
    table_figure_plan.yaml     # optional: planned tables/figures + required evidence fields
  05_evidence/
    paper_cards/            # one file per key paper (JSON)
    extracted_tables/       # table rows (CSV/JSON)
    chunks/                 # optional (RAG): chunked full text with page pointers
      chunks.jsonl
  06_draft/
    00_outline.md
    10_intro.md
    20_taxonomy.md
    30_comparison.md
    40_challenges.md
    50_future.md
    90_conclusion.md
    claims_map.csv          # optional: draft claims -> evidence pointers (paper_id + page/chunk)
  07_quality/
    rubric_report.md
    traceability_report.md  # optional: missing-evidence list for claims/tables
```

## `00_project.yaml` (minimal)

- `project_slug`: string
- `title_working`: string
- `review_type`: must be `survey_tutorial`
- `topic_statement`: 3–8 sentences
- `audience`: string
- `scope_in`: list of bullets
- `scope_out`: list of bullets
- `target_venues`: list of strings (optional)

## `01_search_terms.yaml`

- `seed_terms`: list of strings
- `synonyms`: map term -> list
- `queries`:
  - `scopus`: string
  - `wos`: string
  - `pubmed`: string
  - `cnki`: string

## Canonical papers schema (`papers_canonical.csv`)

Columns (recommended):

- `paper_id` (stable local id)
- `title`
- `year`
- `authors`
- `venue`
- `abstract`
- `keywords`
- `doi`
- `url`
- `source_database` (scopus/wos/pubmed/cnki/other)

## `03_screening/abstract_decisions.csv`

Columns:

- `paper_id`
- `decision` (`include` / `exclude` / `uncertain`)
- `reason_tag` (one of a controlled list)
- `notes` (free text; optional)

## `04_taxonomy/taxonomy.yaml`

- `taxonomy_name`
- `version`
- `nodes`: recursive list with `id`, `name`, `definition`, `inclusion_rules`, `exclusion_rules`

## `05_evidence/paper_cards/*.json`

One “paper card” per key paper (especially those used heavily in tables):

- `paper_id`
- `claims`: list (claim text + supporting evidence pointer)
- `evidence_pointers`: optional list (page/chunk ids once chunking is enabled)
- `method_summary`
- `assumptions`
- `datasets`
- `metrics`
- `compute`
- `reproducibility`
- `limitations`
