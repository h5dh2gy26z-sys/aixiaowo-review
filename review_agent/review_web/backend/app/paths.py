from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


_SLUG_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_\-]{0,63}$")


@dataclass(frozen=True)
class WorkspacePaths:
    workspace_root: Path
    review_projects_root: Path
    baseline_root: Path
    baseline_tools_root: Path
    baseline_template_root: Path
    frontend_dist_root: Path


def get_workspace_paths() -> WorkspacePaths:
    # review_agent/review_web/backend/app/paths.py -> repo root
    workspace_root = Path(__file__).resolve().parents[4]
    review_projects_root = workspace_root / "review_agent" / "review_projects"
    baseline_root = workspace_root / "review_agent" / "review_writing_baseline"
    baseline_tools_root = baseline_root / "tools"
    baseline_template_root = baseline_root / "project_template"
    frontend_dist_root = workspace_root / "review_agent" / "review_web" / "frontend" / "dist"

    return WorkspacePaths(
        workspace_root=workspace_root,
        review_projects_root=review_projects_root,
        baseline_root=baseline_root,
        baseline_tools_root=baseline_tools_root,
        baseline_template_root=baseline_template_root,
        frontend_dist_root=frontend_dist_root,
    )


def validate_slug(slug: str) -> str:
    slug = (slug or "").strip()
    if not slug or not _SLUG_RE.match(slug):
        raise ValueError("invalid slug (allowed: letters/digits/_/-, max 64 chars)")
    return slug


def safe_relpath(rel: str) -> Path:
    rel = (rel or "").strip().replace("\\", "/")
    p = Path(rel)
    if not rel or p.is_absolute():
        raise ValueError("invalid path")
    if ".." in p.parts:
        raise ValueError("path traversal is not allowed")
    return p


def resolve_under(root: Path, rel: Path) -> Path:
    resolved_root = root.resolve()
    resolved = (resolved_root / rel).resolve()
    if not resolved.is_relative_to(resolved_root):
        raise ValueError("path escapes root")
    return resolved

