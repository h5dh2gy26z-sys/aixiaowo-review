from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


_CLAIM_RE = re.compile(r"^\s*CLAIM:\s*(.+?)\s*$", re.IGNORECASE)
_EVID_RE = re.compile(r"\[EVIDENCE:([A-Za-z0-9_\-]+):p(\d+)\]")


def _iter_md_files(draft_dir: Path) -> list[Path]:
    if not draft_dir.exists():
        return []
    return sorted([p for p in draft_dir.glob("*.md") if p.is_file()])


def _read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8", errors="replace").splitlines()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project_dir", type=Path)
    args = parser.parse_args()

    root = args.project_dir.resolve()
    draft_dir = root / "06_draft"
    quality_dir = root / "07_quality"
    quality_dir.mkdir(parents=True, exist_ok=True)

    claims_map_csv = draft_dir / "claims_map.csv"
    trace_report_md = quality_dir / "traceability_report.md"

    claim_rows: list[dict] = []
    missing: list[str] = []

    for md in _iter_md_files(draft_dir):
        for i, ln in enumerate(_read_lines(md), start=1):
            m = _CLAIM_RE.match(ln)
            if not m:
                continue
            claim = m.group(1).strip()
            evid = _EVID_RE.search(ln)
            if evid:
                paper_id, page = evid.group(1), evid.group(2)
                claim_rows.append(
                    {
                        "draft_file": md.name,
                        "line": str(i),
                        "claim": claim,
                        "paper_id": paper_id,
                        "evidence": f"{paper_id}:p{page}",
                    }
                )
            else:
                missing.append(f"{md.name}:{i} {claim}")
                claim_rows.append(
                    {
                        "draft_file": md.name,
                        "line": str(i),
                        "claim": claim,
                        "paper_id": "",
                        "evidence": "",
                    }
                )

    # write claims_map.csv
    with claims_map_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["draft_file", "line", "claim", "paper_id", "evidence"])
        w.writeheader()
        for r in claim_rows:
            w.writerow(r)

    # report
    lines = ["# Traceability Report", ""]
    lines.append("## Convention")
    lines.append("- Write claims as: `CLAIM: ... [EVIDENCE:paper_id:p12]`")
    lines.append("- Evidence refers to `05_evidence/chunks/chunks.jsonl` chunk ids like `paper_id:p12`.")
    lines.append("")
    lines.append(f"## Claims found: {len(claim_rows)}")
    lines.append(f"## Missing evidence: {len(missing)}")
    lines.append("")
    if missing:
        lines.append("### Missing list")
        for x in missing[:200]:
            lines.append(f"- {x}")
        if len(missing) > 200:
            lines.append(f"- ... ({len(missing)-200} more)")
        lines.append("")

    trace_report_md.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote: {claims_map_csv}")
    print(f"Wrote: {trace_report_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

