"""Tests for the proof gate: PASS, FAIL and the never-a-pass SKIPPED rule."""

from __future__ import annotations

from selfproof.gates.base import GateContext, Verdict
from selfproof.gates.proof import ProofGate


def _ctx(tmp_path, commands):
    return GateContext(
        repo_root=tmp_path,
        commit_sha="c0ffee" * 6,
        config={"proof": {"commands": commands, "timeout": 60}},
    )


def test_all_commands_pass(tmp_path):
    ctx = _ctx(tmp_path, [["python", "-c", "print('ok')"]])
    result = ProofGate().run(ctx)
    assert result.verdict is Verdict.PASS
    assert ctx.commit_sha[:12] in result.summary


def test_failing_command_fails(tmp_path):
    ctx = _ctx(tmp_path, [["python", "-c", "import sys; sys.exit(1)"]])
    result = ProofGate().run(ctx)
    assert result.verdict is Verdict.FAIL


def test_missing_tool_is_skipped_not_passed(tmp_path):
    ctx = _ctx(tmp_path, [["this-tool-does-not-exist-xyz"]])
    result = ProofGate().run(ctx)
    assert result.verdict is Verdict.SKIPPED
    assert result.verdict is not Verdict.PASS


def test_fail_wins_over_skip(tmp_path):
    ctx = _ctx(tmp_path, [
        ["this-tool-does-not-exist-xyz"],
        ["python", "-c", "import sys; sys.exit(2)"],
    ])
    result = ProofGate().run(ctx)
    assert result.verdict is Verdict.FAIL
