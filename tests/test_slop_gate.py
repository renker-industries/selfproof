"""Corpus tests for the slop gate."""

from __future__ import annotations

from pathlib import Path

from selfproof.gates.slop import SlopGate

CORPUS = Path(__file__).parent / "corpus"
BAD = CORPUS / "bad" / "slop"
GOOD = CORPUS / "good" / "slop"


def test_flags_every_bad_example():
    gate = SlopGate()
    for path in sorted(BAD.glob("*.py")):
        findings = gate._scan(path, path.name)
        assert findings, f"missed slop in {path.name}"


def test_passes_every_good_example():
    gate = SlopGate()
    for path in sorted(GOOD.glob("*.py")):
        findings = gate._scan(path, path.name)
        assert not findings, f"false positive on {path.name}: {findings}"


def test_detects_each_category():
    gate = SlopGate()
    findings = "\n".join(gate._scan(BAD / "slop_example.py", "slop_example.py"))
    assert "placeholder marker" in findings
    assert "no assertion" in findings
    assert "placeholder" in findings  # the '...' body
    assert "broad except" in findings
