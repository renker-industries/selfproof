"""Tests for the token module: honest net-saving and sample-size gating."""

from __future__ import annotations

from selfproof.tokens import aggregate, net_saving, report
from selfproof.tokens.meter import TokenUsage


def _rec(bi, bo, ai, ao, overhead=0):
    return {
        "baseline_tokens": {"input": bi, "output": bo},
        "actual_tokens": {"input": ai, "output": ao},
        "overhead_tokens": overhead,
    }


def test_net_saving_formula():
    base = TokenUsage(1000, 1000)
    actual = TokenUsage(600, 400)
    assert net_saving(base, actual, overhead=100) == 900


def test_unmeasured_run_yields_none():
    assert net_saving(TokenUsage(None, 10), TokenUsage(5, 5), 0) is None


def test_below_sample_floor_shows_no_percentage():
    stats = aggregate([_rec(1000, 1000, 500, 500) for _ in range(3)])
    assert stats.status == "insufficient data"
    assert stats.net_percent is None
    text = report(stats)
    assert "insufficient data" in text
    assert "%" not in text


def test_measured_sample_reports_saving():
    stats = aggregate([_rec(1000, 1000, 500, 500, overhead=100) for _ in range(6)])
    assert stats.status == "preliminary"  # 5 <= n < 20
    assert stats.mean_saving == 900
    assert stats.net_percent is not None
    assert "%" in report(stats)


def test_unmeasured_runs_are_counted_separately():
    records = [_rec(1000, 1000, 500, 500) for _ in range(5)]
    records.append({"baseline_tokens": None, "actual_tokens": None, "overhead_tokens": 0})
    stats = aggregate(records)
    assert stats.n == 5
    assert stats.unmeasured == 1
