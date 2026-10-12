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


def test_protocol_members_with_ellipsis_are_not_placeholders(tmp_path):
    source = (
        "from typing import Generic, Protocol, TypeVar\n"
        "import typing\n"
        "T = TypeVar('T')\n"
        "class A(Protocol):\n"
        "    def one(self) -> int: ...\n"
        "class B(typing.Protocol):\n"
        "    def two(self) -> int:\n"
        "        '''doc'''\n"
        "        ...\n"
        "class C(Protocol[T]):\n"
        "    async def three(self) -> T: ...\n"
    )
    path = tmp_path / "protocols.py"
    path.write_text(source, encoding="utf-8")
    assert SlopGate()._scan(path, "protocols.py") == []


def test_ellipsis_in_plain_class_is_still_flagged(tmp_path):
    source = "class Plain:\n    def todo(self) -> int: ...\n\ndef stub() -> None: ...\n"
    path = tmp_path / "plain.py"
    path.write_text(source, encoding="utf-8")
    findings = SlopGate()._scan(path, "plain.py")
    assert len(findings) == 2
    assert all("placeholder" in f for f in findings)


def test_detects_each_category():
    gate = SlopGate()
    findings = "\n".join(gate._scan(BAD / "slop_example.py", "slop_example.py"))
    assert "placeholder marker" in findings
    assert "no assertion" in findings
    assert "placeholder" in findings  # the '...' body
    assert "broad except" in findings
