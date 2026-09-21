"""Run gates against the current commit and record evidence.

The runner is the single place that turns a gate result into a ledger entry: it
resolves the commit SHA, hashes the gate output, and appends one evidence entry
per gate. The dashboard and CLI read only from the ledger it writes.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from ..gates import GATES, GateContext, GateResult, Verdict
from ..gates.base import run_command
from .config import load_config
from .ledger import Ledger


@dataclass(frozen=True)
class RunReport:
    """The outcome of running a set of gates."""

    commit_sha: str
    results: list[GateResult]
    entry_ids: list[str]

    @property
    def blocking(self) -> bool:
        """True if any gate produced a blocking verdict (FAIL or ERROR)."""
        return any(r.blocking for r in self.results)

    @property
    def has_skips(self) -> bool:
        """True if any gate was SKIPPED (relevant to the release rule)."""
        return any(r.verdict is Verdict.SKIPPED for r in self.results)


def current_commit(repo_root: Path) -> str:
    """Return the current commit SHA, or ``"uncommitted"`` if none exists yet."""
    code, out = run_command(["git", "rev-parse", "HEAD"], repo_root)
    if code == 0 and out.strip():
        return out.strip()
    return "uncommitted"


def run_gates(
    repo_root: str | Path,
    gate_names: list[str] | None = None,
    *,
    actor_kind: str = "agent",
    actor_name: str = "claude-code opus-4-8",
) -> RunReport:
    """Run the named gates (default: all registered) and record each result.

    Args:
        repo_root: Repository root.
        gate_names: Gate names to run; ``None`` runs every registered gate.
        actor_kind: ``human``, ``agent`` or ``ci`` for the ledger.
        actor_name: The actor's name for the ledger.

    Returns:
        A :class:`RunReport` with the results and the ledger entry ids.

    Raises:
        KeyError: If a requested gate name is not registered.
    """
    root = Path(repo_root)
    cfg = load_config(root)
    stage = cfg.get("stage", "seed")
    commit_sha = current_commit(root)
    ledger = Ledger(root / cfg["ledger"]["path"])

    names = gate_names if gate_names is not None else list(GATES)
    results: list[GateResult] = []
    entry_ids: list[str] = []

    ctx = GateContext(repo_root=root, commit_sha=commit_sha, config=cfg)
    for name in names:
        gate = GATES[name]()
        result = gate.run(ctx)
        results.append(result)
        output_sha = hashlib.sha256(result.output.encode("utf-8")).hexdigest()
        entry = ledger.record(
            actor_kind=actor_kind,
            actor_name=actor_name,
            commit_sha=commit_sha,
            gate=result.gate,
            command=result.command,
            exit_code=result.exit_code,
            output_sha256=output_sha,
            verdict=result.verdict.value,
            stage=stage,
        )
        entry_ids.append(entry.id)

    return RunReport(commit_sha=commit_sha, results=results, entry_ids=entry_ids)
