"""Adapter declarations and honest capability levels (concept section 7).

An adapter connects one coding agent to Selfproof's enforcement. Every adapter
declares exactly one capability level, and the level is only as high as the
evidence supports:

- **L0** — rules file only. The agent is asked to follow the rules. Advisory.
- **L1** — enforced at commit and in CI through git hooks and required checks.
- **L2** — enforced during the session through the agent's native hooks, plus L1.

The floor for any agent that commits to the repository is L1, because the git
hooks and CI apply regardless of the agent. L2 is claimed only when a verified
native hook mechanism is wired and tested; until then an agent stays at L1 and
the reason is recorded in :attr:`Adapter.notes`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class CapabilityLevel(Enum):
    """The three honest enforcement levels."""

    L0 = "L0"
    L1 = "L1"
    L2 = "L2"


@dataclass(frozen=True)
class Adapter:
    """A declaration of how one agent is connected to Selfproof.

    Attributes:
        name: The agent's identifier (e.g. ``claude_code``).
        level: The verified :class:`CapabilityLevel`.
        rules_file: The rules file generated for this agent, or ``None`` if it
            reads no rules file.
        evidence: Why the declared level is justified (what is actually wired).
        notes: Honest limitations, and what a higher level would require.
    """

    name: str
    level: CapabilityLevel
    rules_file: str | None
    evidence: str
    notes: str = ""
    verified_docs: bool = field(default=False)
