"""Tests for fleet mode parsing and classification (no network)."""

from __future__ import annotations

from selfproof.fleet import FleetSnapshot, parse_repo_list, report
from selfproof.fleet.scan import IN_SCOPE

_JSON = """[
  {"name": "selfproof", "visibility": "PRIVATE", "primaryLanguage": {"name": "Python"}},
  {"name": "renkervault", "visibility": "PUBLIC", "primaryLanguage": {"name": "TypeScript"}},
  {"name": "profile", "visibility": "PUBLIC", "primaryLanguage": null}
]"""


def test_parse_sets_full_name_and_language():
    repos = parse_repo_list("renker-industries", _JSON)
    names = {r.full_name for r in repos}
    assert "renker-industries/selfproof" in names
    langs = {r.full_name: r.language for r in repos}
    assert langs["renker-industries/profile"] == "none"  # null language


def test_in_scope_flags_only_charter_repos():
    repos = parse_repo_list("renker-industries", _JSON)
    in_scope = [r.full_name for r in repos if r.in_scope]
    assert in_scope == ["renker-industries/selfproof"]
    assert "renker-industries/selfproof" in IN_SCOPE


def test_snapshot_aggregates():
    repos = parse_repo_list("renker-industries", _JSON)
    snap = FleetSnapshot(repos=repos)
    assert snap.total == 3
    assert snap.by_visibility["private"] == 1
    assert snap.by_visibility["public"] == 2


def test_report_states_the_honest_limit():
    snap = FleetSnapshot(repos=parse_repo_list("acc", _JSON))
    text = report(snap)
    assert "read-only" in text
    assert "not implemented yet" in text
