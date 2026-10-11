"""Gate subprocesses must not inherit credentials from the environment."""

from __future__ import annotations

import sys
from pathlib import Path

from selfproof.gates.base import run_command, scrubbed_env


def test_credentials_are_removed_and_normal_vars_kept() -> None:
    env = {
        "PATH": "/bin",
        "SystemRoot": "C:\\Windows",
        "ANTHROPIC_API_KEY": "x",
        "OPENAI_API_KEY": "x",
        "GITHUB_TOKEN": "x",
        "MY_SERVICE_SECRET": "x",
        "DB_PASSWORD": "x",
    }
    assert scrubbed_env(env) == {"PATH": "/bin", "SystemRoot": "C:\\Windows"}


def test_allow_list_keeps_named_variable() -> None:
    env = {"FOO_API_KEY": "x", "BAR_TOKEN": "y", "SELFPROOF_ENV_ALLOW": "foo_api_key"}
    out = scrubbed_env(env)
    assert "FOO_API_KEY" in out
    assert "BAR_TOKEN" not in out


def test_run_command_child_does_not_see_secret(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "leak-canary")
    code, out = run_command(
        [sys.executable, "-c", "import os; print(os.environ.get('ANTHROPIC_API_KEY'))"],
        tmp_path,
    )
    assert code == 0
    assert "leak-canary" not in out
    assert out.strip() == "None"
