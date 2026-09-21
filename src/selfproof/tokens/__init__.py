"""Token measurement module (concept section 8).

Measures the net token saving of the token layer from paired control runs. No
number is invented: percentages come only from loaded benchmark files, and
unmeasured runs are never counted as zero.
"""

from __future__ import annotations

from .bench import BenchStats, aggregate, load_records, report
from .meter import TokenUsage, net_saving

__all__ = [
    "TokenUsage",
    "net_saving",
    "BenchStats",
    "aggregate",
    "load_records",
    "report",
]
