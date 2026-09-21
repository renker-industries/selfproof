"""Tests for the evidence ledger built on the kernel audit chain."""

from __future__ import annotations

import pytest

from selfproof.core.ledger import Ledger, LedgerError


def _record(ledger: Ledger, gate: str, verdict: str) -> None:
    ledger.record(
        actor_kind="agent",
        actor_name="claude-code test",
        commit_sha="deadbeef" * 5,
        gate=gate,
        command="python -m pytest -q",
        exit_code=0,
        output_sha256="a" * 64,
        verdict=verdict,
        stage="seed",
    )


def test_record_and_read_roundtrip(tmp_path):
    ledger = Ledger(tmp_path / "ledger.jsonl")
    _record(ledger, "proof", "PASS")
    _record(ledger, "language", "PASS")
    entries = ledger.read_all()
    assert [e.gate for e in entries] == ["proof", "language"]
    assert entries[0].verdict == "PASS"
    assert entries[0].actor_kind == "agent"
    assert entries[1].prev_hash == entries[0].hash


def test_verify_passes_on_intact_chain(tmp_path):
    ledger = Ledger(tmp_path / "ledger.jsonl")
    _record(ledger, "proof", "PASS")
    _record(ledger, "proof", "FAIL")
    ledger.verify()  # must not raise
    assert ledger.head() == ledger.read_all()[-1].hash


def test_verify_detects_tampering(tmp_path):
    path = tmp_path / "ledger.jsonl"
    ledger = Ledger(path)
    _record(ledger, "proof", "PASS")
    _record(ledger, "proof", "PASS")
    lines = path.read_text(encoding="utf-8").splitlines()
    # Flip a recorded verdict without recomputing the chain.
    lines[0] = lines[0].replace('"PASS"', '"FAIL"', 1)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    with pytest.raises(LedgerError):
        ledger.verify()


def test_head_is_genesis_when_empty(tmp_path):
    ledger = Ledger(tmp_path / "empty.jsonl")
    assert ledger.head() == "0" * 64
    assert ledger.read_all() == []
