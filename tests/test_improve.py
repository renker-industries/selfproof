"""Tests for the improvement engine: measure, regressions, ratchet."""

from __future__ import annotations

import json
from pathlib import Path

from selfproof.improve import _BASELINE, measure, ratchet, regressions

REPO = Path(__file__).resolve().parents[1]


def test_measure_has_expected_metrics():
    m = measure(REPO)
    assert m["gates"] >= 8
    assert m["adapters"] >= 6
    assert m["test_functions"] > 0
    assert m["runtime_dependencies"] == 0


def test_regressions_detects_a_drop():
    assert regressions({"gates": 8}, {"gates": 7})
    assert regressions({"runtime_dependencies": 0}, {"runtime_dependencies": 1})


def test_no_regression_when_flat_or_improved():
    assert regressions({"gates": 8}, {"gates": 8}) == []
    assert regressions({"gates": 8}, {"gates": 9}) == []


def test_ratchet_writes_then_reports_no_change(tmp_path):
    moved, problems = ratchet(tmp_path)
    assert moved and problems == []
    assert (tmp_path / _BASELINE).exists()
    moved2, problems2 = ratchet(tmp_path)
    assert not moved2
    assert any("no change" in p for p in problems2)


def test_ratchet_refuses_a_regression(tmp_path):
    baseline_path = tmp_path / _BASELINE
    baseline_path.parent.mkdir(parents=True, exist_ok=True)
    # A baseline claiming more gates than exist forces a regression.
    baseline_path.write_text(json.dumps({"metrics": {"gates": 999}}), encoding="utf-8")
    moved, problems = ratchet(tmp_path)
    assert not moved
    assert any("gates" in p and "->" in p for p in problems)
