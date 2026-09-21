"""Collect dashboard metrics from the ledger and git (concept section 9).

The dashboard reads only from the evidence ledger, the git history (for the
self-built share) and the token benchmarks. Every number here is derived, never
invented; when data is missing the field is reported as such rather than as
zero-with-confidence.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from ..core.config import load_config
from ..core.ledger import Ledger
from ..gates.base import run_command
from ..tokens import aggregate, load_records


@dataclass(frozen=True)
class DashboardData:
    """Aggregated, presentation-ready metrics for the dashboard."""

    total_checks: int
    verdicts: dict[str, int]
    by_gate: dict[str, dict[str, int]]
    prevented: int
    agent_commits: int
    human_commits: int
    bench_status: str
    bench_summary: str
    generated: str = ""
    warnings: list[str] = field(default_factory=list)

    @property
    def self_built_share(self) -> float | None:
        """Return the agent share of commits (0..1), or None if there are none."""
        total = self.agent_commits + self.human_commits
        return self.agent_commits / total if total else None


def collect(repo_root: str | Path) -> DashboardData:
    """Gather dashboard metrics for the repository at ``repo_root``."""
    root = Path(repo_root)
    cfg = load_config(root)
    ledger = Ledger(root / cfg["ledger"]["path"])
    entries = ledger.read_all()

    verdicts: Counter[str] = Counter()
    by_gate: dict[str, Counter[str]] = {}
    for entry in entries:
        verdicts[entry.verdict] += 1
        by_gate.setdefault(entry.gate, Counter())[entry.verdict] += 1
    prevented = verdicts.get("FAIL", 0)

    agent, human = _commit_authors(root)
    bench = aggregate(load_records(root / "docs" / "reports" / "benchmarks"))

    warnings: list[str] = []
    if not entries:
        warnings.append("ledger is empty on this machine; run `selfproof build` to populate it")

    return DashboardData(
        total_checks=len(entries),
        verdicts=dict(verdicts),
        by_gate={g: dict(c) for g, c in by_gate.items()},
        prevented=prevented,
        agent_commits=agent,
        human_commits=human,
        bench_status=bench.status,
        bench_summary=_bench_line(bench),
        warnings=warnings,
    )


def _commit_authors(root: Path) -> tuple[int, int]:
    code, out = run_command(["git", "log", "--format=%b%x1e"], root)
    if code is None or code != 0:
        return 0, 0
    agent = human = 0
    for block in out.split("\x1e"):
        low = block.lower()
        if "built-by: agent" in low:
            agent += 1
        elif "built-by: human" in low:
            human += 1
    return agent, human


def _bench_line(bench) -> str:
    if bench.n < 5:
        return f"insufficient data (n={bench.n}); no percentage shown"
    pct = bench.net_percent
    part = f", {pct:.1f}% of baseline" if pct is not None else ""
    return f"{bench.mean_saving:.0f} tokens/task net ({bench.status}, n={bench.n}{part})"
