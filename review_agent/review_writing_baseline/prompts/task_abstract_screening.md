# Task prompt: abstract-level triage

Goal: Given a batch of papers (title + abstract + year), classify into `include/exclude/uncertain` using project scope.

Inputs:

- `00_project.yaml`
- A CSV-like list with fields: `paper_id,title,year,abstract,keywords,venue,doi`

Output:

- Append rows to `03_screening/abstract_decisions.csv` with:
  - `paper_id,decision,reason_tag,notes`

Decision rules:

- Use `exclude` when clearly out-of-scope.
- Use `uncertain` when missing info, ambiguous methods, or unclear domain match.
- Keep `reason_tag` from a controlled set:
  - `out_of_scope_domain`
  - `wrong_problem`
  - `non_method_paper`
  - `insufficient_detail`
  - `not_peer_reviewed` (if applicable)
  - `duplicate`
  - `other`

