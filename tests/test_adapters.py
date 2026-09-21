"""Tests for the adapter registry and the generated capability matrix."""

from __future__ import annotations

from pathlib import Path

from selfproof.adapters import ADAPTERS, CapabilityLevel

MATRIX = Path(__file__).resolve().parents[1] / "docs" / "reference" / "capability-matrix.md"


def test_every_adapter_has_evidence_and_valid_level():
    assert ADAPTERS
    for name, adapter in ADAPTERS.items():
        assert adapter.name == name
        assert isinstance(adapter.level, CapabilityLevel)
        assert adapter.evidence.strip(), f"{name} has no evidence"


def test_no_l2_is_claimed_without_wired_hooks():
    # Honesty: no adapter claims L2 yet (no native session hook is wired/tested).
    assert all(a.level is not CapabilityLevel.L2 for a in ADAPTERS.values())


def test_git_is_the_enforcement_floor():
    assert ADAPTERS["git"].level is CapabilityLevel.L1


def test_ollama_is_l0_with_a_stated_limit():
    assert ADAPTERS["ollama"].level is CapabilityLevel.L0
    assert ADAPTERS["ollama"].notes.strip()


def test_capability_matrix_lists_every_adapter():
    text = MATRIX.read_text(encoding="utf-8")
    for name in ADAPTERS:
        assert f"`{name}`" in text, f"{name} missing from the capability matrix"
