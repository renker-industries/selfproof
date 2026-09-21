"""Integration tests for the test_weakening gate against a temporary git repo."""

from __future__ import annotations

import subprocess

from selfproof.gates.base import GateContext, Verdict
from selfproof.gates.test_weakening import TestWeakeningGate


def _git(repo, *args):
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


def _repo(tmp_path):
    repo = tmp_path / "r"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "t@example.com")
    _git(repo, "config", "user.name", "t")
    _git(repo, "config", "commit.gpgsign", "false")
    return repo


def _ctx(repo):
    return GateContext(repo_root=repo, commit_sha="x", config={})


def test_pass_when_no_new_commits(tmp_path):
    repo = _repo(tmp_path)
    (repo / "test_a.py").write_text("def test_a():\n    assert 1 == 1\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "init")
    # HEAD == merge-base(main, HEAD) -> nothing to compare
    result = TestWeakeningGate().run(_ctx(repo))
    assert result.verdict is Verdict.PASS


def test_flags_removed_assertion(tmp_path):
    repo = _repo(tmp_path)
    (repo / "test_a.py").write_text("def test_a():\n    assert 1 == 1\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "init")
    _git(repo, "checkout", "-q", "-b", "weaken")
    (repo / "test_a.py").write_text("def test_a():\n    pass\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "remove assertion")
    result = TestWeakeningGate().run(_ctx(repo))
    assert result.verdict is Verdict.FAIL
    assert "removed assertion" in result.output


def test_flags_added_skip_marker(tmp_path):
    repo = _repo(tmp_path)
    (repo / "test_a.py").write_text("def test_a():\n    assert True\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "init")
    _git(repo, "checkout", "-q", "-b", "skip")
    (repo / "test_a.py").write_text(
        "import pytest\n\n\n@pytest.mark.skip\ndef test_a():\n    assert True\n", encoding="utf-8"
    )
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "add skip")
    result = TestWeakeningGate().run(_ctx(repo))
    assert result.verdict is Verdict.FAIL
    assert "skip" in result.output
