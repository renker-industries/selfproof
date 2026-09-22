"""Tests for `selfproof init` scaffolding and the gate-subset config."""

from __future__ import annotations

from selfproof.core.config import DEFAULT_CONFIG, load_config
from selfproof.scaffold import _PROJECT_GATES, _detect_proof_commands, init


def test_detect_proof_commands_empty_without_tests(tmp_path):
    commands, _ = _detect_proof_commands(tmp_path)
    assert commands == []


def test_detect_proof_commands_pytest_with_tests(tmp_path):
    (tmp_path / "tests").mkdir()
    commands, _ = _detect_proof_commands(tmp_path)
    assert commands and "pytest" in commands[0]


def test_init_creates_config_rules_and_hooks(tmp_path):
    written = init(tmp_path)
    assert "selfproof.toml" in written
    assert "rules/agents.yaml" in written
    for name in ("CLAUDE.md", "AGENTS.md", "GEMINI.md"):
        assert (tmp_path / name).exists(), name
    for hook in ("pre-commit", "commit-msg", "pre-push"):
        assert (tmp_path / "hooks" / hook).exists(), hook


def test_init_writes_a_project_gate_subset(tmp_path):
    init(tmp_path)
    cfg = load_config(tmp_path)
    assert cfg["gates"]["enabled"] == _PROJECT_GATES
    assert cfg["ledger"]["path"] == ".selfproof/ledger.jsonl"


def test_init_skips_existing_config_without_force(tmp_path):
    init(tmp_path)
    (tmp_path / "selfproof.toml").write_text("stage = 'kept'\n", encoding="utf-8")
    written = init(tmp_path)
    assert "selfproof.toml" not in written
    assert "stage = 'kept'" in (tmp_path / "selfproof.toml").read_text(encoding="utf-8")


def test_default_config_runs_all_gates():
    assert DEFAULT_CONFIG["gates"]["enabled"] is None
