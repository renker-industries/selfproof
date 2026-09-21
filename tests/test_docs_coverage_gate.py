"""Tests for the docs_coverage gate: the real repo passes; gaps are detected."""

from __future__ import annotations

import ast
from pathlib import Path

from selfproof.gates.base import GateContext, Verdict
from selfproof.gates.docs_coverage import DocsCoverageGate

REPO = Path(__file__).resolve().parents[1]


def test_real_repo_passes():
    ctx = GateContext(repo_root=REPO, commit_sha="x", config={})
    result = DocsCoverageGate().run(ctx)
    assert result.verdict is Verdict.PASS, result.output


def test_missing_readme_is_flagged(tmp_path):
    pkg = tmp_path / "src" / "selfproof"
    (pkg / "sub").mkdir(parents=True)
    (pkg / "sub" / "mod.py").write_text('"""doc."""\n', encoding="utf-8")
    findings = DocsCoverageGate._dir_readmes(pkg, tmp_path)
    assert any("missing README.md" in f for f in findings)


def test_class_name_attr_reads_gate_name():
    tree = ast.parse('class G:\n    name = "slop"\n')
    node = tree.body[0]
    assert DocsCoverageGate._class_name_attr(node) == "slop"


def test_missing_docstring_is_flagged(tmp_path):
    pkg = tmp_path / "src" / "selfproof"
    pkg.mkdir(parents=True)
    (pkg / "m.py").write_text("def public():\n    return 1\n", encoding="utf-8")
    findings = DocsCoverageGate()._docstrings(pkg, tmp_path)
    assert any("missing module docstring" in f for f in findings)
    assert any("has no docstring" in f for f in findings)
