from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project_slug", type=str)
    parser.add_argument(
        "--dest-root",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "review_projects",
        help="Destination root for projects (default: review_agent/review_projects/)",
    )
    parser.add_argument(
        "--template",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "project_template",
        help="Template directory (default: review_agent/review_writing_baseline/project_template/)",
    )
    args = parser.parse_args()

    slug = args.project_slug.strip()
    if not slug:
        raise SystemExit("project_slug is required")

    dest = args.dest_root / slug
    if dest.exists():
        raise SystemExit(f"destination already exists: {dest}")

    shutil.copytree(args.template, dest)

    project_yaml = dest / "00_project.yaml"
    if project_yaml.exists():
        text = project_yaml.read_text(encoding="utf-8")
        project_yaml.write_text(text.replace("demo_survey", slug), encoding="utf-8")

    print(f"Scaffolded: {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
