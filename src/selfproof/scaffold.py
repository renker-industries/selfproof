"""`selfproof init`: set Selfproof up in any project so any AI codes to the rules.

It writes, into the target repository:

- ``selfproof.toml`` with a project-appropriate gate set and detected test
  command;
- ``rules/agents.yaml`` and the generated ``CLAUDE.md`` / ``AGENTS.md`` /
  ``GEMINI.md`` so Claude Code, Codex, Cursor, Aider and Gemini CLI all read the
  same rules;
- git hooks that run the gates at commit and push (adapter level L1).

Everything is embedded here, so it also works from the packaged binary with no
source checkout. Existing files are left untouched unless ``force`` is set.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from .core.rules import write_generated

# The default rules shipped into a new project (same content as this repo's
# rules/agents.yaml). Edit rules/agents.yaml in the target and regenerate.
DEFAULT_RULES_YAML = """\
# Source of truth for the per-agent rules files.
# CLAUDE.md, AGENTS.md and GEMINI.md are GENERATED from this file.
title: Project rules (enforced by Selfproof)
intro: Generated from rules/agents.yaml. Edit the source, then run selfproof rules generate.
rules:
  - id: english-only
    text: All files, comments, commits and docs are in English.
  - id: evidence-or-planned
    text: Every done/correct/secure claim is backed by a check that ran, or labelled planned.
  - id: no-absolute-claims
    text: Never write absolutely secure, unhackable, guaranteed or bug-free.
  - id: no-slop
    text: No placeholder bodies, TODO markers, error-swallowing except, or assertionless tests.
  - id: small-changes
    text: Smallest change that solves the task; one concern per commit with a Built-by trailer.
  - id: no-weakening
    text: Never weaken or delete a test, assertion or threshold to make something pass.
"""

_HOOK_PRECOMMIT = """\
#!/usr/bin/env bash
# Selfproof pre-commit: fast language check.
set -e
if command -v selfproof >/dev/null 2>&1; then SP=selfproof; else SP="python -m selfproof.cli"; fi
$SP build --gates language
"""

_HOOK_COMMITMSG = """\
#!/usr/bin/env bash
# Selfproof commit-msg: require a Built-by trailer (honest self-built metric).
set -e
if ! grep -qiE '^Built-by:[[:space:]]*(human|agent[[:space:]]+.+)$' "$1"; then
  echo "commit-msg: add 'Built-by: human' or 'Built-by: agent <name> <version>'." >&2
  exit 1
fi
"""

_HOOK_PREPUSH = """\
#!/usr/bin/env bash
# Selfproof pre-push: run the gates and verify the ledger.
set -e
if command -v selfproof >/dev/null 2>&1; then SP=selfproof; else SP="python -m selfproof.cli"; fi
$SP build
$SP ledger verify
"""

_PROJECT_GATES = ["language", "proof", "slop", "security", "test_weakening"]

# Claude Code project settings: run the fast static gates automatically whenever
# Claude finishes a response, so you only talk to the AI and Selfproof checks the
# result on its own. The full gate set still runs at commit via the git hooks.
_CLAUDE_SETTINGS = """\
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "selfproof build --gates language,slop,test_weakening"
          }
        ]
      }
    ]
  }
}
"""


def _detect_proof_commands(root: Path) -> tuple[list, str]:
    """Return (commands, note) guessing how to test the project.

    Only sets a test command when there is something to test, so a project
    without tests passes cleanly instead of failing on an empty test run.
    """
    if (root / "package.json").exists():
        return [["npm", "test", "--silent"]], "detected package.json (npm test)"
    has_tests = (root / "tests").is_dir() or any(root.rglob("test_*.py"))
    if has_tests:
        return [["python", "-m", "pytest", "-q"]], "detected Python tests (pytest)"
    return [], "no tests found yet — add your test command to proof.commands later"


def _toml(commands: list) -> str:
    cmds = ", ".join("[" + ", ".join(f'"{a}"' for a in c) + "]" for c in commands)
    gates = ", ".join(f'"{g}"' for g in _PROJECT_GATES)
    return (
        "# Selfproof configuration for this project.\n"
        'stage = "self-hosted"\n\n'
        "[gates]\n"
        f"enabled = [{gates}]\n\n"
        "[proof]\n"
        f"commands = [{cmds}]\n\n"
        "[security]\n"
        "# Your project need not carry a LICENSE for the security gate to pass.\n"
        "require_license = false\n\n"
        "[ledger]\n"
        'path = ".selfproof/ledger.jsonl"\n'
    )


def init(repo_root: str | Path, *, force: bool = False) -> list[str]:
    """Scaffold Selfproof into ``repo_root``. Returns the paths written."""
    root = Path(repo_root)
    written: list[str] = []

    def write(rel: str, content: str, executable: bool = False) -> None:
        path = root / rel
        if path.exists() and not force:
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        if executable:
            path.chmod(0o755)
        written.append(rel)

    commands, _ = _detect_proof_commands(root)
    write("selfproof.toml", _toml(commands))
    write("rules/agents.yaml", DEFAULT_RULES_YAML)
    # Claude Code native integration: check automatically when the AI finishes.
    write(".claude/settings.json", _CLAUDE_SETTINGS)
    (root / ".selfproof").mkdir(exist_ok=True)

    # Generate the per-agent rules files from the source we just wrote.
    for name in write_generated(root):
        if name not in written:
            written.append(name)

    write("hooks/pre-commit", _HOOK_PRECOMMIT, executable=True)
    write("hooks/commit-msg", _HOOK_COMMITMSG, executable=True)
    write("hooks/pre-push", _HOOK_PREPUSH, executable=True)

    _enable_hooks(root)
    return written


def _enable_hooks(root: Path) -> None:
    """Point git at the hooks/ directory if this is a git repository."""
    try:
        subprocess.run(
            ["git", "config", "core.hooksPath", "hooks"],
            cwd=str(root), check=False, capture_output=True, text=True,
        )
    except FileNotFoundError:
        pass
