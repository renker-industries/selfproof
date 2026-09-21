"""Tests for the dashboard: collection, rendering and export privacy."""

from __future__ import annotations

from selfproof.core.ledger import Ledger
from selfproof.dashboard import collect, render_html, render_terminal


def _seed_ledger(root):
    ledger = Ledger(root / "docs" / "reports" / "ledger.jsonl")
    for gate, verdict in [("proof", "PASS"), ("language", "PASS"), ("slop", "FAIL")]:
        ledger.record(
            actor_kind="agent", actor_name="claude-code test",
            commit_sha="c" * 40, gate=gate, command="x", exit_code=0,
            output_sha256="a" * 64, verdict=verdict, stage="self-hosted",
        )


def test_collect_counts_verdicts(tmp_path):
    _seed_ledger(tmp_path)
    data = collect(tmp_path)
    assert data.total_checks == 3
    assert data.verdicts["PASS"] == 2
    assert data.prevented == 1  # one FAIL


def test_render_html_is_self_contained(tmp_path):
    _seed_ledger(tmp_path)
    out = render_html(collect(tmp_path))
    assert "<title>Selfproof dashboard" in out
    assert "<script" not in out
    assert "http://" not in out and "https://" not in out  # no external resources


def test_export_leaks_no_paths_or_ledger_internals(tmp_path):
    _seed_ledger(tmp_path)
    out = render_html(collect(tmp_path))
    assert str(tmp_path) not in out
    assert ".jsonl" not in out
    assert "a" * 64 not in out  # no raw output hashes


def test_terminal_summary_handles_empty(tmp_path):
    text = render_terminal(collect(tmp_path))
    assert "SELFPROOF DASHBOARD" in text
    assert "no commits" in text  # not a git repo -> no self-built share
