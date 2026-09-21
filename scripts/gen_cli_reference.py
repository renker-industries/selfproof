"""Generate docs/reference/cli.md from the selfproof argument parser.

Run: PYTHONPATH=src python scripts/gen_cli_reference.py
Keeps the CLI reference in sync with the code (concept 10.2, generated docs).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, "src")
sys.path.insert(0, "src/renker_core")

from selfproof.cli import build_parser  # noqa: E402


def render() -> str:
    parser = build_parser()
    lines = ["# CLI reference", "", "Generated from the parser by",
             "`scripts/gen_cli_reference.py`. Do not edit by hand.", ""]
    sub = parser._subparsers._group_actions[0]  # the subcommand action
    for name, p in sub.choices.items():
        lines.append(f"## `selfproof {name}`")
        lines.append("")
        lines.append(p.description or p.format_usage().strip())
        lines.append("")
        for action in p._actions:
            opts = ", ".join(action.option_strings) or action.dest
            if opts == "help":
                continue
            lines.append(f"- `{opts}`: {action.help or ''}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


if __name__ == "__main__":
    Path("docs/reference/cli.md").write_text(render(), encoding="utf-8")
    print("wrote docs/reference/cli.md")
