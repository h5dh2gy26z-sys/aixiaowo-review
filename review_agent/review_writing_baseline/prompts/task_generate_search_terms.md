# Task prompt: generate database search terms (Survey/Tutorial)

Input:

- `00_project.yaml` (topic_statement, scope_in, scope_out)

Output:

- `01_search_terms.yaml` with:
  - `seed_terms`: 10–25 high-signal terms
  - `synonyms`: term -> synonyms/variants
  - `queries`: `scopus`, `wos`, `pubmed`, `cnki`

Rules:

- Queries should be readable and editable.
- Include exclusions that match `scope_out`.
- Prefer English queries for Scopus/WoS/PubMed; CNKI can be Chinese guidance + Chinese/English mixed query.

