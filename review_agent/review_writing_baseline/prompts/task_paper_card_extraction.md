# Task prompt: extract a paper card from full text

Input:

- One paper PDF (or extracted text)
- Its metadata row from `papers_canonical.csv`

Output:

- `05_evidence/paper_cards/<paper_id>.json` with:
  - method_summary
  - claims (claim + evidence snippet pointer)
  - assumptions
  - datasets/metrics/compute
  - limitations
  - reproducibility notes

Rules:

- If you cannot find a field, write `null` and add a short `missing_evidence` note.

