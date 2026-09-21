"""Unit tests for the architecture gate's checks.

The architecture gate's "corpus" is synthetic: import graphs, function sizes and
dependency/ADR pairs are exercised directly, since a file corpus cannot express
cycles or budgets cleanly.
"""

from __future__ import annotations

import ast

from selfproof.gates.architecture import ArchitectureGate


def test_detects_import_cycle():
    graph = {"a": {"b"}, "b": {"a"}}
    findings = ArchitectureGate._cycles(graph)
    assert any("cycle" in f for f in findings)


def test_acyclic_graph_is_clean():
    graph = {"a": {"b"}, "b": {"c"}, "c": set()}
    assert ArchitectureGate._cycles(graph) == []


def test_function_budget_flags_long_function():
    body = "\n".join(f"    x{i} = {i}" for i in range(10))
    source = f"def big():\n{body}\n"
    tree = ast.parse(source)
    findings = ArchitectureGate._func_budget(tree, "m.py", budget=3)
    assert any("big" in f for f in findings)


def test_function_budget_passes_short_function():
    tree = ast.parse("def small():\n    return 1\n")
    assert ArchitectureGate._func_budget(tree, "m.py", budget=80) == []


def test_dependency_without_adr_is_flagged(tmp_path):
    (tmp_path / "pyproject.toml").write_text(
        '[project]\ndependencies = ["requests>=2"]\n', encoding="utf-8"
    )
    (tmp_path / "docs" / "decisions").mkdir(parents=True)
    findings = ArchitectureGate._dependency_adrs(tmp_path)
    assert any("requests" in f for f in findings)


def test_dependency_with_adr_passes(tmp_path):
    (tmp_path / "pyproject.toml").write_text(
        '[project]\ndependencies = ["requests>=2"]\n', encoding="utf-8"
    )
    d = tmp_path / "docs" / "decisions"
    d.mkdir(parents=True)
    (d / "ADR-0009-requests.md").write_text("We adopt requests for X.", encoding="utf-8")
    assert ArchitectureGate._dependency_adrs(tmp_path) == []
