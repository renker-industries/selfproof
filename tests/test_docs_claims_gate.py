"""Corpus tests for the docs_claims gate."""

from __future__ import annotations

from selfproof.gates.docs_claims import DocsClaimsGate


def _scan(text: str) -> list[str]:
    return DocsClaimsGate()._scan(text, "README.md")


def test_flags_forbidden_absolute_claim():
    assert _scan("Our system is unhackable and 100% secure.")


def test_allows_negated_disclaimer():
    assert not _scan("It does not promise 'unhackable' or 'bug-free' code.")


def test_flags_unlabelled_percentage():
    assert _scan("Selfproof saves 80% of tokens.")


def test_allows_labelled_percentage():
    assert not _scan("Selfproof saved 42% (measured, sample size n=20).")


def test_clean_line_passes():
    assert not _scan("Every check is bound to the exact commit.")
