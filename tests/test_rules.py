"""Tests for the rules-as-data source and the generated agent files."""

from __future__ import annotations

from pathlib import Path

from selfproof.core.rules import (
    AGENT_FILES,
    check_generated,
    load_rules,
    render,
    write_generated,
)

REPO = Path(__file__).resolve().parents[1]


def test_load_rules_parses_source():
    data = load_rules(REPO / "rules" / "agents.yaml")
    assert data["title"]
    assert data["intro"]
    ids = {r["id"] for r in data["rules"]}
    assert "english-only" in ids
    assert "no-weakening" in ids


def test_render_includes_header_and_every_rule():
    data = load_rules(REPO / "rules" / "agents.yaml")
    text = render(data, "Claude Code")
    assert text.startswith("<!-- GENERATED")
    for rule in data["rules"]:
        assert rule["id"] in text


def test_committed_files_are_current():
    assert check_generated(REPO) == [], "run scripts/gen_agent_rules.py"


def test_check_detects_drift(tmp_path):
    (tmp_path / "rules").mkdir()
    (tmp_path / "rules" / "agents.yaml").write_text(
        "title: T\nintro: I\nrules:\n  - id: a\n    text: b\n", encoding="utf-8"
    )
    write_generated(tmp_path)
    assert check_generated(tmp_path) == []
    # Hand-edit a generated file -> drift detected.
    first = tmp_path / next(iter(AGENT_FILES.values()))
    first.write_text(first.read_text(encoding="utf-8") + "\nsneaky edit\n", encoding="utf-8")
    drift = check_generated(tmp_path)
    assert any("stale or hand-edited" in d for d in drift)
