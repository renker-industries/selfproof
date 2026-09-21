"""Configuration loading. Zero dependencies: TOML via the stdlib ``tomllib``.

The runtime configuration lives in ``selfproof.toml`` at the repo root. Missing
keys fall back to :data:`DEFAULT_CONFIG`. The rules-as-data files under
``rules/`` (which generate ``CLAUDE.md`` / ``AGENTS.md``) are a separate
concern handled in :mod:`selfproof.core.rules`.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

DEFAULT_CONFIG: dict = {
    "proof": {
        # Commands the `proof` gate runs and binds to the current commit.
        # Each must exit 0 for a PASS. A missing tool is SKIPPED, never PASS.
        "commands": [
            ["python", "-m", "pytest", "-q"],
            ["python", "-m", "ruff", "check", "."],
        ],
        "timeout": 900,
    },
    "language": {
        # Paths (relative, prefix match) excluded from the English-only rule.
        "exclude": [
            "tests/fixtures/non_english/",
            "tests/corpus/bad/",  # intentionally-bad gate examples, tested in isolation
            "src/renker_core/",  # imported kernel; gated in its own repo
            "src/selfproof/gates/data/",  # foreign-language marker data, not prose
            ".git/",
        ],
        # File suffixes treated as text and scanned.
        "text_suffixes": [
            ".py", ".md", ".txt", ".toml", ".yaml", ".yml", ".cfg", ".ini",
            ".rst", ".json", ".sh",
        ],
    },
    "ledger": {"path": "docs/reports/ledger.jsonl"},
    "stage": "seed",
}


def load_config(repo_root: str | Path) -> dict:
    """Return the merged configuration for the repository at ``repo_root``.

    Args:
        repo_root: The repository root directory.

    Returns:
        The default configuration deep-merged with ``selfproof.toml`` if present.
    """
    root = Path(repo_root)
    cfg = _deep_copy(DEFAULT_CONFIG)
    toml_path = root / "selfproof.toml"
    if toml_path.exists():
        with open(toml_path, "rb") as handle:
            override = tomllib.load(handle)
        _deep_merge(cfg, override)
    return cfg


def _deep_copy(value: dict) -> dict:
    return {k: (_deep_copy(v) if isinstance(v, dict) else v) for k, v in value.items()}


def _deep_merge(base: dict, override: dict) -> None:
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value
