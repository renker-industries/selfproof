"""Generate CLAUDE.md, AGENTS.md and GEMINI.md from rules/agents.yaml.

Run: PYTHONPATH=src python scripts/gen_agent_rules.py
"""
from __future__ import annotations

import sys

sys.path.insert(0, "src")

from selfproof.core.rules import write_generated  # noqa: E402

if __name__ == "__main__":
    for name in write_generated("."):
        print("wrote", name)
