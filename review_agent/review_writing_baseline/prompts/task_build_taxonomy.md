# Task prompt: build/update taxonomy

Inputs:

- `00_project.yaml`
- Included papers list (paper_id + title + abstract)
- Existing `04_taxonomy/taxonomy.yaml` (optional)

Output:

- Updated `04_taxonomy/taxonomy.yaml` with:
  - clear node definitions
  - inclusion/exclusion rules per node

Constraints:

- Minimize overlap between sibling nodes.
- Taxonomy must be usable to classify every included paper.

