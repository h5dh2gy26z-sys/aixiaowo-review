from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml


def _read_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) if path.exists() else {}


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def _write_md(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project_dir", type=Path)
    args = parser.parse_args()

    root = args.project_dir.resolve()
    taxonomy = _read_yaml(root / "04_taxonomy" / "taxonomy.yaml")
    plan = _read_yaml(root / "04_taxonomy" / "table_figure_plan.yaml")

    nodes = ((taxonomy.get("nodes") or [{}])[0].get("children") or []) if taxonomy else []
    tables = plan.get("tables") or []
    figures = plan.get("figures") or []

    intro = [
        "# 10 Introduction",
        "",
        "- 本综述/教程的动机与范围",
        "- 本文贡献：taxonomy、对比表、最佳实践与开放问题",
        "",
    ]
    _write_md(root / "06_draft" / "10_intro.md", "\n".join(intro))

    taxo_lines = ["# 20 Taxonomy", "", "## 2.1 Taxonomy 结构", ""]
    for n in nodes:
        if not isinstance(n, dict) or not n.get("id"):
            continue
        taxo_lines.append(f"- `{n['id']}` **{n.get('name','')}**：{n.get('definition','')}")
    taxo_lines.extend(["", "## 2.2 说明", "- 这里先给出 v0.1（abstract-based），后续会根据 paper cards 迭代。", ""])
    _write_md(root / "06_draft" / "20_taxonomy.md", "\n".join(taxo_lines))

    cmp_lines = ["# 30 Comparison", "", "## 3.1 计划表格/图", ""]
    for t in tables:
        cmp_lines.append(f"- Table `{t.get('id','')}`: {t.get('title','')} (schema: {t.get('schema','')})")
    for f in figures:
        cmp_lines.append(f"- Figure `{f.get('id','')}`: {f.get('title','')}")
    cmp_lines.extend(
        [
            "",
            "## 3.2 代表性论文卡片（paper cards）",
            "",
            "从 `05_evidence/paper_cards/*.json` 中挑选每个 taxonomy leaf 的代表性论文，填充对比表。",
            "",
        ]
    )
    _write_md(root / "06_draft" / "30_comparison.md", "\n".join(cmp_lines))

    # keep other sections as-is if user edited; only scaffold if missing
    for name, title, bullets in [
        ("40_challenges.md", "40 Challenges", ["- 局限性与失败模式", "- 威胁有效性与复现难点"]),
        ("50_future.md", "50 Future Directions", ["- 开放问题", "- 值得投入的方向与基准建议"]),
        ("90_conclusion.md", "90 Conclusion", ["- 核心结论", "- 实践建议与 takeaways"]),
    ]:
        p = root / "06_draft" / name
        if p.exists():
            continue
        _write_md(p, "\n".join([f"# {title}", "", *bullets, ""]))

    print("Wrote drafts: 06_draft/10_intro.md, 20_taxonomy.md, 30_comparison.md (and scaffolded others if missing)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

