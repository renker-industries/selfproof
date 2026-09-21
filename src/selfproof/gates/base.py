"""Gate primitives: the four honest verdicts and the gate contract.

A gate is any check that inspects a change and returns exactly one
:class:`Verdict`. The core rule of Selfproof lives here: a missing tool, no
network, or a timeout is ``SKIPPED`` or ``ERROR`` -- never ``PASS`` (concept
section 4.1, principle 6).
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path


class Verdict(StrEnum):
    """The only four results a check may return."""

    PASS = "PASS"
    FAIL = "FAIL"
    SKIPPED = "SKIPPED"
    ERROR = "ERROR"


@dataclass(frozen=True)
class GateResult:
    """The outcome of running one gate.

    Attributes:
        gate: The gate's name (used as the ledger ``gate`` field).
        verdict: One of :class:`Verdict`.
        summary: One line describing the outcome.
        command: The command that produced the result, or ``""`` if none.
        exit_code: Process exit code, or ``None`` when no process was run.
        output: Captured output whose SHA-256 is recorded as evidence.
        details: Machine-readable findings (paths, counts) for the dashboard.
    """

    gate: str
    verdict: Verdict
    summary: str
    command: str = ""
    exit_code: int | None = None
    output: str = ""
    details: dict = field(default_factory=dict)

    @property
    def blocking(self) -> bool:
        """True when this result must block a change (FAIL or ERROR)."""
        return self.verdict in (Verdict.FAIL, Verdict.ERROR)


@dataclass(frozen=True)
class GateContext:
    """What a gate needs to run.

    Attributes:
        repo_root: Absolute path to the repository root.
        commit_sha: The commit the result is bound to.
        config: The resolved Selfproof configuration.
    """

    repo_root: Path
    commit_sha: str
    config: dict


class Gate:
    """Base class for all gates. Subclasses set :attr:`name` and implement
    :meth:`run`."""

    name: str = "gate"

    def run(self, ctx: GateContext) -> GateResult:  # pragma: no cover - abstract
        raise NotImplementedError


def run_command(cmd: list[str], cwd: Path, timeout: int = 600) -> tuple[int | None, str]:
    """Run ``cmd`` and return ``(exit_code, combined_output)``.

    A missing executable yields ``(None, ...)`` so callers can map it to
    ``SKIPPED`` or ``ERROR`` rather than a false ``PASS``. A timeout yields
    ``(None, ...)`` as well.

    Args:
        cmd: The command and its arguments.
        cwd: Working directory.
        timeout: Seconds before the command is killed.

    Returns:
        A tuple of the exit code (``None`` if the tool was missing or timed out)
        and the combined stdout+stderr text.
    """
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except FileNotFoundError:
        return None, f"tool not found: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return None, f"timeout after {timeout}s: {' '.join(cmd)}"
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")
