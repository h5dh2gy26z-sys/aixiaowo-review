from __future__ import annotations

import argparse
import csv
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import yaml


_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "can",
    "for",
    "from",
    "has",
    "have",
    "in",
    "into",
    "is",
    "it",
    "its",
    "may",
    "of",
    "on",
    "or",
    "our",
    "paper",
    "review",
    "survey",
    "that",
    "the",
    "their",
    "this",
    "to",
    "using",
    "we",
    "with",
    "within",
    "without",
}


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.strip().lower()).strip("_")


def _tokenize(text: str) -> list[str]:
    text = text.lower()
    tokens = re.findall(r"[a-z0-9][a-z0-9\-_]{1,}", text)
    out: list[str] = []
    for t in tokens:
        t = t.strip("-_")
        if len(t) < 3:
            continue
        if t in _STOPWORDS:
            continue
        out.append(t)
    return out


def _read_csv_dicts(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(str(path))
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return []
        return list(reader)


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


@dataclass(frozen=True)
class Paper:
    paper_id: str
    title: str
    abstract: str
    year: int | None
    doi: str
    url: str

    @property
    def text(self) -> str:
        return f"{self.title}\n{self.abstract}".strip()


def _parse_year(s: str) -> int | None:
    s = (s or "").strip()
    if not s:
        return None
    try:
        y = int(float(s))
    except ValueError:
        return None
    if 1900 <= y <= 2100:
        return y
    return None


def _load_papers(papers_csv: Path) -> dict[str, Paper]:
    rows = _read_csv_dicts(papers_csv)
    out: dict[str, Paper] = {}
    for r in rows:
        pid = (r.get("paper_id") or "").strip()
        if not pid:
            continue
        out[pid] = Paper(
            paper_id=pid,
            title=(r.get("title") or "").strip(),
            abstract=(r.get("abstract") or "").strip(),
            year=_parse_year(r.get("year") or ""),
            doi=(r.get("doi") or "").strip(),
            url=(r.get("url") or "").strip(),
        )
    return out


def _load_included_ids(decisions_csv: Path) -> set[str]:
    rows = _read_csv_dicts(decisions_csv)
    included: set[str] = set()
    for r in rows:
        pid = (r.get("paper_id") or "").strip()
        decision = (r.get("decision") or "").strip().lower()
        if not pid:
            continue
        if decision in {"include", "included", "yes", "y", "1", "true"}:
            included.add(pid)
    return included


def _top_terms(papers: list[Paper], max_terms: int) -> list[str]:
    unigram = Counter()
    bigram = Counter()
    for p in papers:
        toks = _tokenize(p.text)
        unigram.update(toks)
        for a, b in zip(toks, toks[1:]):
            if a in _STOPWORDS or b in _STOPWORDS:
                continue
            bigram.update([f"{a} {b}"])

    candidates: list[str] = []
    for t, _ in bigram.most_common(max_terms * 3):
        if len(candidates) >= max_terms:
            break
        a, b = t.split(" ", 1)
        if a == b:
            continue
        candidates.append(t)

    for t, _ in unigram.most_common(max_terms * 3):
        if len(candidates) >= max_terms:
            break
        if t in candidates:
            continue
        candidates.append(t)

    return candidates[:max_terms]


def _term_keywords(term: str) -> list[str]:
    parts = term.split()
    if len(parts) == 1:
        return [parts[0]]
    return parts


def _build_taxonomy(terms: list[str]) -> dict:
    children = []
    for i, term in enumerate(terms, start=1):
        node_id = f"t{i:02d}_{_slug(term)[:24] or 'topic'}"
        children.append(
            {
                "id": node_id,
                "name": term.title(),
                "definition": f"Abstract-derived cluster for: {term}",
                "inclusion_rules": [f"mentions: {', '.join(_term_keywords(term))}"],
                "exclusion_rules": [],
                "children": [],
            }
        )

    children.append(
        {
            "id": "t99_other",
            "name": "Other / General",
            "definition": "Fallback node when abstracts do not strongly match any cluster.",
            "inclusion_rules": [],
            "exclusion_rules": [],
            "children": [],
        }
    )

    return {
        "taxonomy_name": "Abstract-derived taxonomy (v0.1)",
        "version": "0.1.0",
        "nodes": [
            {
                "id": "root",
                "name": "Root",
                "definition": "Top-level grouping",
                "inclusion_rules": [],
                "exclusion_rules": [],
                "children": children,
            }
        ],
    }


def _score_paper_for_term(p: Paper, term: str) -> int:
    text = p.text.lower()
    parts = term.split()
    if len(parts) == 1:
        return text.count(parts[0])
    # bigram term: require all parts, count rough min-occurrence
    counts = [text.count(part) for part in parts]
    return min(counts) if counts else 0


def _classify(papers: list[Paper], terms: list[str], taxonomy_children: list[dict]) -> list[dict]:
    term_to_node = {}
    for term, node in zip(terms, taxonomy_children, strict=False):
        term_to_node[term] = node

    rows: list[dict] = []
    for p in papers:
        scored = [(term, _score_paper_for_term(p, term)) for term in terms]
        scored.sort(key=lambda x: x[1], reverse=True)
        best_term, best_score = scored[0] if scored else ("", 0)
        total = sum(s for _, s in scored) or 0

        if best_score <= 0:
            node_id = "t99_other"
            confidence = 0.2
            rationale = "no strong keyword match; fallback to Other"
        else:
            node_id = term_to_node[best_term]["id"]
            confidence = min(0.95, 0.35 + (best_score / max(1, total)) * 0.6)
            rationale = f"best match='{best_term}' score={best_score} total={total}"

        rows.append(
            {
                "paper_id": p.paper_id,
                "taxonomy_node_id": node_id,
                "confidence": f"{confidence:.2f}",
                "rationale": rationale,
            }
        )
    return rows


def _rank_fulltext_priority(papers: list[Paper]) -> list[dict]:
    def score(p: Paper) -> tuple[int, int, int]:
        year = p.year or 0
        # prefer: recent papers first; missing DOI/URL slightly higher urgency
        miss = 1 if (not p.doi and not p.url) else 0
        abs_len = len(p.abstract or "")
        return (year, miss, abs_len)

    ordered = sorted(papers, key=score, reverse=True)
    rows: list[dict] = []
    for idx, p in enumerate(ordered, start=1):
        needs = [
            "problem/task definition",
            "method details (architecture/algorithm)",
            "datasets",
            "metrics",
            "compute/training setup",
            "reproducibility (code, seeds, hyperparams)",
            "limitations/failure modes",
        ]
        reason_bits = []
        if p.year:
            reason_bits.append(f"recent_year={p.year}")
        if not p.doi and not p.url:
            reason_bits.append("missing_doi_url")
        if p.abstract:
            reason_bits.append(f"abstract_len={len(p.abstract)}")
        rows.append(
            {
                "paper_id": p.paper_id,
                "priority": str(idx),
                "reason": "; ".join(reason_bits) or "ranked by heuristics",
                "extraction_needs": ", ".join(needs),
            }
        )
    return rows


def _write_taxonomy_yaml(path: Path, taxonomy: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(taxonomy, sort_keys=False, allow_unicode=True), encoding="utf-8")


def _write_table_figure_plan(path: Path, taxonomy_children: list[dict]) -> None:
    plan = {
        "version": "0.1.0",
        "tables": [
            {
                "id": "T1_method_comparison",
                "title": "Method comparison (by taxonomy leaf)",
                "schema": "method_comparison",
                "notes": "Populate after full-text extraction; start from representative papers per taxonomy node.",
            },
            {
                "id": "T2_dataset_benchmark",
                "title": "Dataset / benchmark overview",
                "schema": "dataset_benchmark",
                "notes": "Collect dataset name, size, split, tasks, metrics, common baselines.",
            },
            {
                "id": "T3_decision_matrix",
                "title": "Practical decision matrix",
                "schema": "decision_matrix",
                "notes": "When to choose which approach; include constraints like compute, latency, data availability.",
            },
            {
                "id": "T4_taxonomy_overview",
                "title": "Taxonomy overview table",
                "schema": "taxonomy_overview",
                "notes": "One row per taxonomy node; short definition + representative papers.",
            },
        ],
        "figures": [
            {
                "id": "F1_taxonomy_tree",
                "title": "Taxonomy tree",
                "notes": "Rendered from 04_taxonomy/taxonomy.yaml.",
            },
            {
                "id": "F2_pipeline",
                "title": "Workflow pipeline figure",
                "notes": "Show end-to-end stages: screening -> taxonomy -> full-text -> tables -> draft -> traceability.",
            },
        ],
        "taxonomy_nodes": [{"id": n["id"], "name": n["name"]} for n in taxonomy_children if n.get("id") != "t99_other"],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(plan, sort_keys=False, allow_unicode=True), encoding="utf-8")


def _write_outline(path: Path, taxonomy_children: list[dict]) -> None:
    leaves = [n for n in taxonomy_children if n.get("id") not in {"t99_other"}]
    lines: list[str] = []
    lines.append("# 00 Outline (auto-generated v0.1)")
    lines.append("")
    lines.append("## 1. Introduction")
    lines.append("- Motivation, scope, and contributions")
    lines.append("")
    lines.append("## 2. Background and Problem Definition")
    lines.append("- Definitions, notation, and evaluation protocol")
    lines.append("")
    lines.append("## 3. Taxonomy Overview")
    lines.append("- Figure: F1_taxonomy_tree")
    for n in leaves:
        lines.append(f"- `{n['id']}` {n['name']}: {n.get('definition','')}")
    lines.append("")
    lines.append("## 4. Methods by Taxonomy Node")
    lines.append("- Table: T1_method_comparison")
    for i, n in enumerate(leaves, start=1):
        lines.append(f"### 4.{i} {n['name']}")
        lines.append("- Key ideas, representative papers, and trade-offs")
        lines.append("")
    lines.append("## 5. Datasets, Benchmarks, and Metrics")
    lines.append("- Table: T2_dataset_benchmark")
    lines.append("")
    lines.append("## 6. Practical Decision Guidance")
    lines.append("- Table: T3_decision_matrix")
    lines.append("")
    lines.append("## 7. Open Problems and Future Directions")
    lines.append("- Limitations, failure modes, and research opportunities")
    lines.append("")
    lines.append("## 8. Conclusion")
    lines.append("- Summary and takeaways")
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project_dir", type=Path, help="review project root, e.g. review_agent/review_projects/demo_survey")
    parser.add_argument("--max-nodes", type=int, default=8, help="max taxonomy children under root (excluding Other)")
    args = parser.parse_args()

    project_root = args.project_dir.resolve()
    papers_csv = project_root / "02_import" / "papers_canonical.csv"
    decisions_csv = project_root / "03_screening" / "abstract_decisions.csv"

    papers_by_id = _load_papers(papers_csv)
    included_ids = _load_included_ids(decisions_csv)
    if not included_ids:
        raise SystemExit(
            "no included papers found in 03_screening/abstract_decisions.csv "
            "(set decision=include for at least one paper_id)"
        )

    included_papers = [papers_by_id[pid] for pid in included_ids if pid in papers_by_id]
    if not included_papers:
        raise SystemExit("included paper_ids not found in 02_import/papers_canonical.csv")

    terms = _top_terms(included_papers, max(3, int(args.max_nodes)))
    taxonomy = _build_taxonomy(terms)
    root_children = taxonomy["nodes"][0]["children"]

    # Outputs
    taxonomy_yaml = project_root / "04_taxonomy" / "taxonomy.yaml"
    paper_classification_csv = project_root / "04_taxonomy" / "paper_classification.csv"
    fulltext_priority_csv = project_root / "04_taxonomy" / "fulltext_priority.csv"
    table_figure_plan_yaml = project_root / "04_taxonomy" / "table_figure_plan.yaml"
    outline_md = project_root / "06_draft" / "00_outline.md"

    _write_taxonomy_yaml(taxonomy_yaml, taxonomy)

    classifications = _classify(included_papers, terms, root_children)
    _write_csv(
        paper_classification_csv,
        fieldnames=["paper_id", "taxonomy_node_id", "confidence", "rationale"],
        rows=classifications,
    )

    priorities = _rank_fulltext_priority(included_papers)
    _write_csv(
        fulltext_priority_csv,
        fieldnames=["paper_id", "priority", "reason", "extraction_needs"],
        rows=priorities,
    )

    _write_table_figure_plan(table_figure_plan_yaml, root_children)
    _write_outline(outline_md, root_children)

    print(f"Wrote: {taxonomy_yaml}")
    print(f"Wrote: {paper_classification_csv}")
    print(f"Wrote: {table_figure_plan_yaml}")
    print(f"Wrote: {fulltext_priority_csv}")
    print(f"Wrote: {outline_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
