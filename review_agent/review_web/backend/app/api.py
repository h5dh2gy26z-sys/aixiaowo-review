from __future__ import annotations

import os
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from .paths import get_workspace_paths, resolve_under, safe_relpath, validate_slug
from .tools import run_python_tool, scaffold_project


router = APIRouter(prefix="/api")


class ProjectCreateRequest(BaseModel):
    slug: str = Field(..., description="project slug, e.g. demo_survey")


class FileWriteRequest(BaseModel):
    content: str


def _http_400(msg: str) -> HTTPException:
    return HTTPException(status_code=400, detail=msg)


def _project_root(slug: str) -> Path:
    paths = get_workspace_paths()
    try:
        slug = validate_slug(slug)
    except ValueError as e:
        raise _http_400(str(e))
    root = paths.review_projects_root / slug
    if not root.exists():
        raise HTTPException(status_code=404, detail=f"project not found: {slug}")
    return root


@router.get("/health")
def health() -> dict:
    return {"ok": True}


@router.get("/projects")
def list_projects() -> dict:
    paths = get_workspace_paths()
    paths.review_projects_root.mkdir(parents=True, exist_ok=True)
    projects = []
    for p in sorted(paths.review_projects_root.iterdir(), key=lambda x: x.name.lower()):
        if not p.is_dir():
            continue
        projects.append({"slug": p.name})
    return {"projects": projects}


@router.get("/projects/{slug}/stats")
def project_stats(slug: str) -> dict:
    root = _project_root(slug)

    def exists(rel: str) -> bool:
        return (root / rel).exists()

    papers_csv = root / "02_import" / "papers_canonical.csv"
    decisions_csv = root / "03_screening" / "abstract_decisions.csv"

    papers_total = 0
    if papers_csv.exists():
        try:
            txt = papers_csv.read_text(encoding="utf-8", errors="replace")
            papers_total = max(0, len([ln for ln in txt.splitlines() if ln.strip()]) - 1)
        except OSError:
            papers_total = 0

    decisions_total = 0
    included_count = 0
    if decisions_csv.exists():
        try:
            txt = decisions_csv.read_text(encoding="utf-8", errors="replace")
            rows = [ln for ln in txt.splitlines() if ln.strip()]
            decisions_total = max(0, len(rows) - 1)
            # naive: decision in second column
            for ln in rows[1:]:
                parts = [p.strip().strip('"') for p in ln.split(",", 2)]
                if len(parts) >= 2 and parts[1].lower() in {"include", "included", "yes", "y", "1", "true"}:
                    included_count += 1
        except OSError:
            decisions_total = 0
            included_count = 0

    artifacts = {
        "project_yaml": exists("00_project.yaml"),
        "papers_canonical": exists("02_import/papers_canonical.csv"),
        "abstract_decisions": exists("03_screening/abstract_decisions.csv"),
        "taxonomy": exists("04_taxonomy/taxonomy.yaml"),
        "paper_classification": exists("04_taxonomy/paper_classification.csv"),
        "fulltext_priority": exists("04_taxonomy/fulltext_priority.csv"),
        "table_figure_plan": exists("04_taxonomy/table_figure_plan.yaml"),
        "outline": exists("06_draft/00_outline.md"),
    }

    return {
        "artifacts": artifacts,
        "counts": {
            "papers_total": papers_total,
            "decisions_total": decisions_total,
            "included_count": included_count,
        },
    }


@router.post("/projects")
def create_project(req: ProjectCreateRequest) -> dict:
    paths = get_workspace_paths()
    try:
        slug = validate_slug(req.slug)
    except ValueError as e:
        raise _http_400(str(e))
    paths.review_projects_root.mkdir(parents=True, exist_ok=True)
    dest = scaffold_project(
        template_root=paths.baseline_template_root,
        dest_root=paths.review_projects_root,
        slug=slug,
    )
    return {"ok": True, "project_root": str(dest)}


@router.get("/projects/{slug}/tree")
def project_tree(slug: str) -> dict:
    root = _project_root(slug)
    entries = []
    for p in sorted(root.rglob("*"), key=lambda x: str(x).lower()):
        if p.is_dir():
            continue
        rel = p.relative_to(root).as_posix()
        # keep it simple; ignore huge/binary by extension
        entries.append({"path": rel, "size": p.stat().st_size})
    return {"files": entries}


_TEXT_EXTS = {".md", ".txt", ".yaml", ".yml", ".json", ".csv"}
_MAX_FILE_BYTES = int(os.environ.get("REVIEW_WEB_MAX_FILE_BYTES", "2097152"))


@router.get("/projects/{slug}/file")
def read_file(slug: str, path: str) -> dict:
    root = _project_root(slug)
    try:
        rel = safe_relpath(path)
        full = resolve_under(root, rel)
    except ValueError as e:
        raise _http_400(str(e))

    if full.suffix.lower() not in _TEXT_EXTS:
        raise _http_400("only text artifacts are supported")
    if not full.exists():
        raise HTTPException(status_code=404, detail="file not found")
    if full.stat().st_size > _MAX_FILE_BYTES:
        raise HTTPException(status_code=413, detail="file too large")
    return {"path": rel.as_posix(), "content": full.read_text(encoding="utf-8", errors="replace")}


@router.put("/projects/{slug}/file")
def write_file(slug: str, path: str, req: FileWriteRequest) -> dict:
    root = _project_root(slug)
    try:
        rel = safe_relpath(path)
        full = resolve_under(root, rel)
    except ValueError as e:
        raise _http_400(str(e))

    if full.suffix.lower() not in _TEXT_EXTS:
        raise _http_400("only text artifacts are supported")
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(req.content, encoding="utf-8")
    return {"ok": True}


@router.post("/projects/{slug}/phase1/run")
def run_phase1(slug: str) -> dict:
    paths = get_workspace_paths()
    root = _project_root(slug)
    tool = paths.baseline_tools_root / "phase1_abstract_to_taxonomy.py"
    proc = run_python_tool(tool, [str(root)])
    return {
        "ok": proc.returncode == 0,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


@router.get("/projects/{slug}/pdfs")
def list_pdfs(slug: str) -> dict:
    root = _project_root(slug)
    pdf_dir = root / "05_evidence" / "pdfs"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    pdfs = []
    for p in sorted(pdf_dir.glob("*.pdf"), key=lambda x: x.name.lower()):
        pdfs.append({"paper_id": p.stem, "filename": p.name, "size": p.stat().st_size})
    return {"pdfs": pdfs}


@router.post("/projects/{slug}/pdfs/{paper_id}")
async def upload_pdf(slug: str, paper_id: str, file: UploadFile = File(...)) -> dict:
    root = _project_root(slug)
    paper_id = (paper_id or "").strip()
    if not paper_id:
        raise _http_400("paper_id is required")
    if not file.filename.lower().endswith(".pdf"):
        raise _http_400("only .pdf is accepted")
    pdf_dir = root / "05_evidence" / "pdfs"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    dest = pdf_dir / f"{paper_id}.pdf"
    data = await file.read()
    if not data:
        raise _http_400("empty file")
    dest.write_bytes(data)
    return {"ok": True, "path": str(dest), "bytes": len(data)}


@router.post("/projects/{slug}/phase2/run")
def run_phase2(slug: str, top_n: int = 10) -> dict:
    paths = get_workspace_paths()
    root = _project_root(slug)
    tool = paths.baseline_tools_root / "phase2_pdf_to_paper_cards.py"
    proc = run_python_tool(tool, [str(root), "--top-n", str(int(top_n))])
    return {
        "ok": proc.returncode == 0,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


@router.post("/projects/{slug}/phase3/run")
def run_phase3(slug: str) -> dict:
    paths = get_workspace_paths()
    root = _project_root(slug)
    tool = paths.baseline_tools_root / "phase3_tables_first_draft.py"
    proc = run_python_tool(tool, [str(root)])
    return {
        "ok": proc.returncode == 0,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


@router.post("/projects/{slug}/phase4/run")
def run_phase4(slug: str) -> dict:
    paths = get_workspace_paths()
    root = _project_root(slug)
    tool = paths.baseline_tools_root / "phase4_traceability_check.py"
    proc = run_python_tool(tool, [str(root)])
    return {
        "ok": proc.returncode == 0,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


@router.post("/projects/{slug}/rubric/check")
def run_rubric(slug: str) -> dict:
    paths = get_workspace_paths()
    root = _project_root(slug)
    tool = paths.baseline_tools_root / "rubric_check.py"
    proc = run_python_tool(tool, [str(root)])
    return {
        "ok": proc.returncode == 0,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }
