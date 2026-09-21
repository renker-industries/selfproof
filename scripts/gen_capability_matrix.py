"""Generate docs/reference/capability-matrix.md from the adapter registry.

Run: PYTHONPATH=src python scripts/gen_capability_matrix.py
Keeps the capability matrix honest and in sync with the code (concept 7, 10.2).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, "src")
sys.path.insert(0, "src/renker_core")

from selfproof.adapters import ADAPTERS  # noqa: E402


def render() -> str:
    lines = [
        "# Capability matrix",
        "",
        "Generated from `src/selfproof/adapters` by",
        "`scripts/gen_capability_matrix.py`. Do not edit by hand.",
        "",
        "Levels: L0 rules-file only (advisory); L1 enforced at commit and in CI;",
        "L2 enforced in-session via native hooks (plus L1).",
        "",
        "| Agent | Level | Rules file | Docs checked | Evidence | Notes |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for name in sorted(ADAPTERS):
        a = ADAPTERS[name]
        lines.append(
            f"| `{a.name}` | {a.level.value} | {a.rules_file or '—'} | "
            f"{'yes' if a.verified_docs else 'no'} | {a.evidence} | {a.notes} |"
        )
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    Path("docs/reference/capability-matrix.md").write_text(render(), encoding="utf-8")
    print("wrote docs/reference/capability-matrix.md")
