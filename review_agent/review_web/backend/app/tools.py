from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


def scaffold_project(*, template_root: Path, dest_root: Path, slug: str) -> Path:
    dest = dest_root / slug
    if dest.exists():
        raise FileExistsError(f"destination already exists: {dest}")
    shutil.copytree(template_root, dest)

    project_yaml = dest / "00_project.yaml"
    if project_yaml.exists():
        text = project_yaml.read_text(encoding="utf-8")
        project_yaml.write_text(text.replace("demo_survey", slug), encoding="utf-8")
    return dest


def run_python_tool(tool_path: Path, args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    if not tool_path.exists():
        raise FileNotFoundError(str(tool_path))
    cmd = [sys.executable, str(tool_path), *args]
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )

