"""Tests for the security gate: secret patterns, licenses and workflow checks."""

from __future__ import annotations

from pathlib import Path

from selfproof.gates.base import GateContext, Verdict
from selfproof.gates.security import _SECRET_PATTERNS, SecurityGate

CORPUS = Path(__file__).parent / "corpus"
REPO = Path(__file__).resolve().parents[1]


def _matches(line: str) -> bool:
    return any(p.search(line) for p in _SECRET_PATTERNS.values())


def test_bad_corpus_lines_are_detected():
    text = (CORPUS / "bad" / "security" / "leaked.txt").read_text(encoding="utf-8")
    hits = [line for line in text.splitlines() if _matches(line)]
    assert len(hits) >= 3  # aws key, private key header, password assignment


def test_good_corpus_has_no_secrets():
    text = (CORPUS / "good" / "security" / "clean.txt").read_text(encoding="utf-8")
    assert not any(_matches(line) for line in text.splitlines())


def test_license_check_flags_forbidden_dependency(tmp_path):
    (tmp_path / "LICENSE").write_text("Apache", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text(
        '[project]\ndependencies = ["somegpl-lib ; GPL-3.0"]\n', encoding="utf-8"
    )
    findings = SecurityGate._license_check(tmp_path)
    assert any("forbidden" in f for f in findings)


def test_license_check_flags_missing_license(tmp_path):
    findings = SecurityGate._license_check(tmp_path)
    assert any("no LICENSE" in f for f in findings)


def test_workflow_check_flags_pull_request_target(tmp_path):
    wf = tmp_path / ".github" / "workflows"
    wf.mkdir(parents=True)
    (wf / "bad.yml").write_text("on: pull_request_target\njobs: {}\n", encoding="utf-8")
    findings = SecurityGate._workflow_check(tmp_path)
    assert any("pull_request_target" in f for f in findings)
    assert any("permissions" in f for f in findings)


def test_workflow_check_passes_hardened_workflow(tmp_path):
    wf = tmp_path / ".github" / "workflows"
    wf.mkdir(parents=True)
    (wf / "ok.yml").write_text(
        "on: push\npermissions:\n  contents: read\njobs: {}\n", encoding="utf-8"
    )
    assert SecurityGate._workflow_check(tmp_path) == []


def test_gate_passes_on_the_repo_with_builtins():
    # Built-in checks are clean on this repo; absent augmenters do not skip it.
    ctx = GateContext(repo_root=REPO, commit_sha="x", config={})
    result = SecurityGate().run(ctx)
    assert result.verdict is Verdict.PASS, result.output
