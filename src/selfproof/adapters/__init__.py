"""The adapter registry (concept section 7).

Each entry is an honest declaration. Levels are conservative: an agent is L1 by
the git+CI floor, and rises to L2 only when native session hooks are wired and
tested (none are yet). Where a capability is claimed, ``verified_docs`` records
whether the agent's current official documentation was checked.
"""

from __future__ import annotations

from .base import Adapter, CapabilityLevel

L0 = CapabilityLevel.L0
L1 = CapabilityLevel.L1

ADAPTERS: dict[str, Adapter] = {
    "git": Adapter(
        name="git",
        level=L1,
        rules_file=None,
        evidence=(
            "commit-msg, pre-commit and pre-push hooks under hooks/ run the gates "
            "and the Built-by trailer check; CI re-runs the gates on every PR."
        ),
        notes="The universal enforcement floor; applies to every agent that commits.",
        verified_docs=True,
    ),
    "claude_code": Adapter(
        name="claude_code",
        level=L1,
        rules_file="CLAUDE.md",
        evidence="Enforced by the git+CI floor. Uses CUSTOS as a plugin in the seed stage.",
        notes=(
            "L2 target: port CUSTOS's native Claude Code hooks and prove they block "
            "in-session. Not wired/tested yet, so declared L1, not L2."
        ),
        verified_docs=False,
    ),
    "codex": Adapter(
        name="codex",
        level=L1,
        rules_file="AGENTS.md",
        evidence="Enforced by the git+CI floor. Reads the AGENTS.md rules file.",
        notes="Session-level hooks unverified; declared L1 until its docs are checked.",
        verified_docs=False,
    ),
    "gemini_cli": Adapter(
        name="gemini_cli",
        level=L1,
        rules_file="GEMINI.md",
        evidence="Enforced by the git+CI floor. Reads the GEMINI.md rules file.",
        notes="Session-level hooks unverified; declared L1 until its docs are checked.",
        verified_docs=False,
    ),
    "cursor": Adapter(
        name="cursor",
        level=L1,
        rules_file="AGENTS.md",
        evidence="Enforced by the git+CI floor. Reads project rules.",
        notes="Session-level hooks unverified; declared L1 until its docs are checked.",
        verified_docs=False,
    ),
    "aider": Adapter(
        name="aider",
        level=L1,
        rules_file="AGENTS.md",
        evidence="Enforced by the git+CI floor. Scriptable, many models.",
        notes="Session-level hooks unverified; declared L1 until its docs are checked.",
        verified_docs=False,
    ),
    "ollama": Adapter(
        name="ollama",
        level=L0,
        rules_file=None,
        evidence="A model runner, not an agent; no commit or hook integration by itself.",
        notes=(
            "Experimental. Ollama runs models; enforcement needs a wrapper that commits "
            "through git (which would raise it to L1). Declared L0 with its limit stated."
        ),
        verified_docs=True,
    ),
}

__all__ = ["Adapter", "CapabilityLevel", "ADAPTERS"]
