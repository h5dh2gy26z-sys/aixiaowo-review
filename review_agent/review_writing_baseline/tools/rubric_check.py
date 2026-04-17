from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class CheckResult:
    check_id: str
    severity: str
    title: str
    passed: bool
    message: str


def _read_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _file_exists(project_root: Path, rel: str) -> tuple[bool, str]:
    p = project_root / rel
    return (p.exists(), str(p))


def _csv_has_columns(project_root: Path, rel: str, required: list[str]) -> tuple[bool, str]:
    p = project_root / rel
    if not p.exists():
        return False, f"missing: {p}"
    with p.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, None)
    if not header:
        return False, f"empty header: {p}"
    header_set = {h.strip() for h in header}
    missing = [c for c in required if c not in header_set]
    if missing:
        return False, f"missing columns {missing} in {p}"
    return True, f"ok: {p}"


def _files_exist_any(project_root: Path, rel_paths: list[str]) -> tuple[bool, str]:
    existing = [str(project_root / rp) for rp in rel_paths if (project_root / rp).exists()]
    if existing:
        return True, f"found {len(existing)} files"
    return False, f"none found among: {rel_paths}"


def _papers_recency_share(project_root: Path, rel: str, years_window: int, min_share: float) -> tuple[bool, str]:
    p = project_root / rel
    if not p.exists():
        return False, f"missing: {p}"
    years: list[int] = []
    with p.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or "year" not in reader.fieldnames:
            return False, f"missing 'year' column in {p}"
        for row in reader:
            y = (row.get("year") or "").strip()
            if not y:
                continue
            try:
                years.append(int(y))
            except ValueError:
                continue
    if not years:
        return False, f"no parseable years in {p}"
    max_year = max(years)
    cutoff = max_year - years_window + 1
    recent = sum(1 for y in years if y >= cutoff)
    share = recent / len(years)
    passed = share >= float(min_share)
    return passed, f"recency share={share:.2f} (cutoff>={cutoff}, max_year={max_year}, n={len(years)})"


def run_check(project_root: Path, check: dict) -> CheckResult:
    check_id = check["id"]
    severity = check["severity"]
    title = check.get("title", "")
    ctype = check["type"]
    params = check.get("params", {})

    if ctype == "file_exists":
        ok, msg = _file_exists(project_root, params["path"])
    elif ctype == "csv_has_columns":
        ok, msg = _csv_has_columns(project_root, params["path"], params["required_columns"])
    elif ctype == "files_exist_any":
        ok, msg = _files_exist_any(project_root, params["paths"])
    elif ctype == "papers_recency_share":
        ok, msg = _papers_recency_share(
            project_root,
            params["path"],
            int(params["years_window"]),
            float(params["min_share"]),
        )
    else:
        ok, msg = False, f"unknown check type: {ctype}"

    return CheckResult(check_id=check_id, severity=severity, title=title, passed=ok, message=msg)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project_dir", type=Path)
    parser.add_argument(
        "--rubric",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "baseline" / "rubric_survey.yaml",
    )
    args = parser.parse_args()

    project_root: Path = args.project_dir.resolve()
    rubric_path: Path = args.rubric.resolve()

    rubric = _read_yaml(rubric_path)
    checks = rubric.get("checks", [])

    results: list[CheckResult] = [run_check(project_root, c) for c in checks]

    blockers_failed = [r for r in results if (not r.passed and r.severity == "blocker")]

    print(f"Rubric: {rubric_path}")
    print(f"Project: {project_root}")
    print("")
    for r in results:
        status = "PASS" if r.passed else "FAIL"
        print(f"[{status}] {r.check_id} ({r.severity}) {r.title} -> {r.message}")

    if blockers_failed:
        print("")
        print(f"BLOCKERS FAILED: {len(blockers_failed)}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

