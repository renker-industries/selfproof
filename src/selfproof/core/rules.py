"""Rules as data: one source, generated per-agent rules files (concept 4.1.3).

``rules/agents.yaml`` is the single source of truth. ``CLAUDE.md``, ``AGENTS.md``
and ``GEMINI.md`` are generated from it, so they never drift or get hand-edited
without detection. A dependency-free reader parses the small, fixed schema
(``title``, ``intro``, and a ``rules`` list of ``id``/``text`` items); no YAML
library is added.

Use :func:`render` to produce a file's content and :func:`check_generated` to
verify the committed files match the source (the CI ``rules`` check).
"""

from __future__ import annotations

from pathlib import Path

AGENT_FILES = {
    "Claude Code": "CLAUDE.md",
    "Codex / Cursor / Aider": "AGENTS.md",
    "Gemini CLI": "GEMINI.md",
}
_HEADER = "<!-- GENERATED from rules/agents.yaml by scripts/gen_agent_rules.py. Do not edit. -->"


def load_rules(path: str | Path) -> dict:
    """Parse ``rules/agents.yaml`` into ``{title, intro, rules: [{id, text}]}``.

    Args:
        path: Path to the rules source file.

    Returns:
        The parsed rules mapping.

    Raises:
        ValueError: If the file does not match the expected small schema.
    """
    text = Path(path).read_text(encoding="utf-8")
    data: dict = {"title": "", "intro": "", "rules": []}
    current: dict | None = None
    in_rules = False
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if not line.startswith(" ") and line.rstrip() == "rules:":
            in_rules = True
            continue
        if not line.startswith(" ") and ":" in line:
            key, _, value = line.partition(":")
            data[key.strip()] = value.strip()
            in_rules = False
            continue
        if in_rules:
            stripped = line.strip()
            if stripped.startswith("- "):
                current = {}
                data["rules"].append(current)
                stripped = stripped[2:]
            if current is None:
                raise ValueError(f"rule field before a list item: {line!r}")
            key, _, value = stripped.partition(":")
            current[key.strip()] = value.strip()
    if not data["rules"]:
        raise ValueError("no rules parsed from source")
    return data


def render(data: dict, agent_label: str) -> str:
    """Render the rules file content for one agent from parsed ``data``."""
    lines = [
        _HEADER,
        "",
        f"# {data['title']}",
        "",
        f"For: {agent_label}",
        "",
        data["intro"],
        "",
        "## Rules",
        "",
    ]
    for rule in data["rules"]:
        lines.append(f"- **{rule['id']}**: {rule['text']}")
    return "\n".join(lines) + "\n"


def check_generated(repo_root: str | Path) -> list[str]:
    """Return a list of drift messages; empty means every generated file is current."""
    root = Path(repo_root)
    data = load_rules(root / "rules" / "agents.yaml")
    drift: list[str] = []
    for label, filename in AGENT_FILES.items():
        expected = render(data, label)
        path = root / filename
        actual = path.read_text(encoding="utf-8") if path.exists() else ""
        if actual != expected:
            reason = "missing" if not path.exists() else "stale or hand-edited"
            drift.append(f"{filename}: {reason}; run scripts/gen_agent_rules.py")
    return drift


def write_generated(repo_root: str | Path) -> list[str]:
    """Write every generated rules file from the source. Returns the paths written."""
    root = Path(repo_root)
    data = load_rules(root / "rules" / "agents.yaml")
    written: list[str] = []
    for label, filename in AGENT_FILES.items():
        (root / filename).write_text(render(data, label), encoding="utf-8")
        written.append(filename)
    return written
