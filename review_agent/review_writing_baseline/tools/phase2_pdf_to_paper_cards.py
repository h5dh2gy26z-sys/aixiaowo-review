from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader


@dataclass(frozen=True)
class PriorityItem:
    paper_id: str
    priority: int
    reason: str
    extraction_needs: str


def _read_csv_dicts(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def _load_priority_list(path: Path) -> list[PriorityItem]:
    if not path.exists():
        return []
    rows = _read_csv_dicts(path)
    out: list[PriorityItem] = []
    for r in rows:
        pid = (r.get("paper_id") or "").strip()
        if not pid:
            continue
        try:
            prio = int((r.get("priority") or "").strip() or "999999")
        except ValueError:
            prio = 999999
        out.append(
            PriorityItem(
                paper_id=pid,
                priority=prio,
                reason=(r.get("reason") or "").strip(),
                extraction_needs=(r.get("extraction_needs") or "").strip(),
            )
        )
    out.sort(key=lambda x: x.priority)
    return out


def _extract_pdf_pages(pdf_path: Path) -> list[str]:
    reader = PdfReader(str(pdf_path))
    pages: list[str] = []
    for p in reader.pages:
        try:
            text = p.extract_text() or ""
        except Exception:
            text = ""
        pages.append(text)
    return pages


def _write_chunks(chunks_path: Path, *, paper_id: str, pages: list[str]) -> list[dict]:
    chunks_path.parent.mkdir(parents=True, exist_ok=True)
    records: list[dict] = []
    with chunks_path.open("a", encoding="utf-8") as f:
        for i, text in enumerate(pages, start=1):
            rec = {
                "chunk_id": f"{paper_id}:p{i}",
                "paper_id": paper_id,
                "page": i,
                "text": text,
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            records.append(rec)
    return records


def _mk_card(
    *,
    paper_id: str,
    extraction_needs: str,
    pdf_path: Path,
    chunks: list[dict],
) -> dict:
    snippet = ""
    for c in chunks:
        t = (c.get("text") or "").strip()
        if t:
            snippet = t[:1200]
            break
    return {
        "paper_id": paper_id,
        "source_pdf": pdf_path.name,
        "extraction_needs": extraction_needs,
        "method_summary": "",
        "assumptions": [],
        "datasets": [],
        "metrics": [],
        "compute": "",
        "reproducibility": "",
        "limitations": [],
        "claims": [],
        "evidence_pointers": [{"chunk_id": c["chunk_id"], "page": c["page"]} for c in chunks[: min(5, len(chunks))]],
        "raw_text_snippet": snippet,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project_dir", type=Path)
    parser.add_argument("--top-n", type=int, default=10)
    args = parser.parse_args()

    root = args.project_dir.resolve()
    priority_csv = root / "04_taxonomy" / "fulltext_priority.csv"
    pdf_dir = root / "05_evidence" / "pdfs"
    cards_dir = root / "05_evidence" / "paper_cards"
    chunks_dir = root / "05_evidence" / "chunks"
    chunks_jsonl = chunks_dir / "chunks.jsonl"

    items = _load_priority_list(priority_csv)
    if not items:
        raise SystemExit("missing or empty: 04_taxonomy/fulltext_priority.csv")

    pdf_dir.mkdir(parents=True, exist_ok=True)
    cards_dir.mkdir(parents=True, exist_ok=True)
    chunks_dir.mkdir(parents=True, exist_ok=True)

    processed = 0
    skipped_missing = []
    for it in items[: max(1, int(args.top_n))]:
        pdf_path = pdf_dir / f"{it.paper_id}.pdf"
        if not pdf_path.exists():
            skipped_missing.append(it.paper_id)
            continue
        pages = _extract_pdf_pages(pdf_path)
        chunks = _write_chunks(chunks_jsonl, paper_id=it.paper_id, pages=pages)
        card = _mk_card(paper_id=it.paper_id, extraction_needs=it.extraction_needs, pdf_path=pdf_path, chunks=chunks)
        (cards_dir / f"{it.paper_id}.json").write_text(json.dumps(card, ensure_ascii=False, indent=2), encoding="utf-8")
        processed += 1

    print(f"Processed paper cards: {processed}")
    if skipped_missing:
        print(f"Missing PDFs (place under 05_evidence/pdfs/<paper_id>.pdf): {', '.join(skipped_missing)}")
    print(f"Wrote/updated: {chunks_jsonl}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

