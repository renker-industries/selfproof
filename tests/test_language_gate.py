"""Corpus tests for the language gate.

The gate must flag every known-bad example and pass every known-good example.
These tests exercise the detector directly, so no git repository is required.
"""

from __future__ import annotations

from pathlib import Path

from selfproof.gates.language import LanguageGate

CORPUS = Path(__file__).parent / "corpus"
BAD = CORPUS / "bad" / "language"
GOOD = CORPUS / "good" / "language"


def test_flags_every_bad_example():
    for path in sorted(BAD.glob("*")):
        assert LanguageGate._german_lines(path), f"missed known-bad file: {path.name}"


def test_passes_every_good_example():
    for path in sorted(GOOD.glob("*")):
        assert not LanguageGate._german_lines(path), f"false positive on: {path.name}"


def test_umlaut_and_stopword_rules_both_fire():
    assert LanguageGate._german_lines(BAD / "german_umlaut.md")
    assert LanguageGate._german_lines(BAD / "german_stopwords.md")
