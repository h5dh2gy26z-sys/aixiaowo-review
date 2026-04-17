from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class ImportedRun:
    deduped_records: list[dict[str, Any]]
    decisions: list[dict[str, Any]]
    config_snapshot: dict[str, Any] | None


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def load_screening_output(screening_output_dir: Path) -> ImportedRun:
    deduped_path = screening_output_dir / "deduped_records.json"
    decisions_path = screening_output_dir / "screening_decisions.json"
    config_path = screening_output_dir / "config.snapshot.json"

    deduped = _read_json(deduped_path)
    decisions = _read_json(decisions_path)
    config = _read_json(config_path) if config_path.exists() else None

    if not isinstance(deduped, list):
        raise ValueError(f"deduped_records.json must be a list: {deduped_path}")
    if not isinstance(decisions, list):
        raise ValueError(f"screening_decisions.json must be a list: {decisions_path}")
    if config is not None and not isinstance(config, dict):
        raise ValueError(f"config.snapshot.json must be an object: {config_path}")

    return ImportedRun(deduped_records=deduped, decisions=decisions, config_snapshot=config)


def write_papers_canonical_csv(*, project_dir: Path, deduped_records: list[dict[str, Any]], overwrite: bool) -> Path:
    out_dir = project_dir / "02_import"
    _ensure_dir(out_dir)
    out_path = out_dir / "papers_canonical.csv"

    if out_path.exists() and not overwrite:
        return out_path

    fieldnames = [
        "paper_id",
        "title",
        "year",
        "authors",
        "venue",
        "abstract",
        "keywords",
        "doi",
        "url",
        "source_database",
    ]
    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in deduped_records:
            writer.writerow(
                {
                    "paper_id": (r.get("paper_id") or "").strip(),
                    "title": (r.get("title") or "").strip(),
                    "year": r.get("year"),
                    "authors": (r.get("authors") or "").strip(),
                    "venue": (r.get("journal") or r.get("venue") or "").strip(),
                    "abstract": (r.get("abstract") or "").strip(),
                    "keywords": json.dumps(r.get("keywords") or [], ensure_ascii=False),
                    "doi": (r.get("doi") or "").strip(),
                    "url": (r.get("url") or "").strip(),
                    "source_database": "",
                }
            )
    return out_path


def write_abstract_decisions_csv(*, project_dir: Path, decisions: list[dict[str, Any]], overwrite: bool) -> Path:
    out_dir = project_dir / "03_screening"
    _ensure_dir(out_dir)
    out_path = out_dir / "abstract_decisions.csv"

    if out_path.exists() and not overwrite:
        return out_path

    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["paper_id", "decision", "reason_tag", "notes"])
        writer.writeheader()
        for d in decisions:
            writer.writerow(
                {
                    "paper_id": (d.get("paper_id") or "").strip(),
                    "decision": (d.get("decision") or "").strip(),
                    "reason_tag": (d.get("reason") or "").strip(),
                    "notes": (d.get("notes") or "").strip(),
                }
            )
    return out_path


def maybe_update_project_yaml(*, project_dir: Path, config_snapshot: dict[str, Any] | None, overwrite: bool) -> Path:
    out_path = project_dir / "00_project.yaml"
    if not out_path.exists():
        return out_path
    if config_snapshot is None:
        return out_path

    if not overwrite:
        return out_path

    payload = yaml.safe_load(out_path.read_text(encoding="utf-8")) or {}
    criteria = (((config_snapshot.get("criteria") or {}) if isinstance(config_snapshot, dict) else {}) or {})  # type: ignore[assignment]

    topic = (criteria.get("topic") or "").strip()
    inclusion = criteria.get("inclusion") or []
    exclusion = criteria.get("exclusion") or []

    if topic:
        payload["topic_statement"] = payload.get("topic_statement") or topic
    if isinstance(inclusion, list) and inclusion:
        payload.setdefault("scope_in", [])
    if isinstance(exclusion, list) and exclusion:
        payload.setdefault("scope_out", [])

    out_path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Import a Wenxian screening output directory into a Survey/Tutorial review project.")
    parser.add_argument("--screening-output-dir", required=True, type=Path)
    parser.add_argument("--project-dir", required=True, type=Path)
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing target artifacts.")
    args = parser.parse_args()

    screening_dir: Path = args.screening_output_dir.resolve()
    project_dir: Path = args.project_dir.resolve()
    overwrite: bool = bool(args.overwrite)

    if not screening_dir.exists():
        raise SystemExit(f"screening output dir not found: {screening_dir}")
    if not project_dir.exists():
        raise SystemExit(f"project dir not found: {project_dir}")

    imported = load_screening_output(screening_dir)
    papers_path = write_papers_canonical_csv(project_dir=project_dir, deduped_records=imported.deduped_records, overwrite=overwrite)
    decisions_path = write_abstract_decisions_csv(project_dir=project_dir, decisions=imported.decisions, overwrite=overwrite)
    maybe_update_project_yaml(project_dir=project_dir, config_snapshot=imported.config_snapshot, overwrite=False)

    print(f"Wrote: {papers_path}")
    print(f"Wrote: {decisions_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

