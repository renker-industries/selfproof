"""Benchmark aggregation for the token module (concept section 8).

Reads paired runs (a control run without the token layer and a run with it) from
JSONL benchmark files and reports the net saving with sample size and method.
Honesty rules enforced here:

- A percentage is produced only from loaded records, never hard-coded.
- Below ``n = 5`` the report says ``insufficient data`` and shows no percentage.
- Below ``n = 20`` the result is labelled ``preliminary``.
- Unmeasured runs are excluded from the statistics and counted separately.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

from .meter import TokenUsage, net_saving

_MIN_SAMPLE = 5
_PRELIMINARY = 20


@dataclass(frozen=True)
class BenchStats:
    """Aggregated benchmark statistics."""

    n: int
    unmeasured: int
    mean_saving: float | None
    stdev_saving: float | None
    mean_baseline: float | None

    @property
    def status(self) -> str:
        """Return 'insufficient data', 'preliminary' or 'measured'."""
        if self.n < _MIN_SAMPLE:
            return "insufficient data"
        if self.n < _PRELIMINARY:
            return "preliminary"
        return "measured"

    @property
    def net_percent(self) -> float | None:
        """Return the net saving as a percentage, or None if not reportable."""
        if self.n < _MIN_SAMPLE or not self.mean_baseline:
            return None
        if self.mean_saving is None:
            return None
        return 100.0 * self.mean_saving / self.mean_baseline


def load_records(directory: str | Path) -> list[dict]:
    """Load every benchmark record from ``*.jsonl`` files under ``directory``."""
    base = Path(directory)
    records: list[dict] = []
    if not base.exists():
        return records
    for path in sorted(base.glob("*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def aggregate(records: list[dict]) -> BenchStats:
    """Aggregate paired benchmark records into :class:`BenchStats`."""
    savings: list[int] = []
    baselines: list[int] = []
    unmeasured = 0
    for rec in records:
        baseline = TokenUsage.from_dict(rec.get("baseline_tokens"))
        actual = TokenUsage.from_dict(rec.get("actual_tokens"))
        overhead = int(rec.get("overhead_tokens", 0))
        saving = net_saving(baseline, actual, overhead)
        if saving is None or baseline.total is None:
            unmeasured += 1
            continue
        savings.append(saving)
        baselines.append(baseline.total)

    n = len(savings)
    mean_saving = sum(savings) / n if n else None
    mean_baseline = sum(baselines) / n if n else None
    stdev = (
        math.sqrt(sum((s - mean_saving) ** 2 for s in savings) / (n - 1))
        if n > 1 and mean_saving is not None
        else None
    )
    return BenchStats(
        n=n, unmeasured=unmeasured, mean_saving=mean_saving,
        stdev_saving=stdev, mean_baseline=mean_baseline,
    )


def report(stats: BenchStats) -> str:
    """Render an honest benchmark report; no percentage below the sample floor."""
    lines = [
        "Token benchmark report",
        f"  sample size n: {stats.n}   unmeasured runs: {stats.unmeasured}",
        f"  status:        {stats.status}",
    ]
    if stats.n < _MIN_SAMPLE:
        lines.append("  net saving:    insufficient data (need n >= 5); no percentage shown")
        return "\n".join(lines)
    pct = stats.net_percent
    lines.append(
        f"  net saving:    {stats.mean_saving:.0f} tokens/task"
        + (f" ({pct:.1f}% of baseline)" if pct is not None else "")
    )
    if stats.stdev_saving is not None:
        lines.append(f"  stdev:         {stats.stdev_saving:.0f} tokens")
    return "\n".join(lines)
