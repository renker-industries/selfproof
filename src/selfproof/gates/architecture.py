"""The ``architecture`` gate: layering, cycles, budgets and dependency hygiene.

Dependency-free static checks over the ``selfproof`` package (the imported
kernel is excluded):

- **Layering:** gate modules are leaves; a module under ``src/selfproof/gates/``
  must not import ``selfproof.core`` or ``selfproof.cli``.
- **Import cycles:** the intra-package import graph must be acyclic.
- **Budgets:** a Python file may not exceed the line budget, and a function may
  not exceed the function-line budget (a simple size proxy for complexity).
- **Dependencies:** every runtime dependency in ``pyproject.toml`` needs an ADR
  line under ``docs/decisions/`` (registry/age/maintainer checks are recorded
  there). Zero dependencies passes trivially.
"""

from __future__ import annotations

import ast
import tomllib
from pathlib import Path

from .base import Gate, GateContext, GateResult, Verdict

_DEFAULTS = {"file_max_lines": 400, "func_max_lines": 80, "package_root": "src/selfproof"}


class ArchitectureGate(Gate):
    """Enforce layering, acyclic imports, size budgets and dependency ADRs."""

    name = "architecture"

    def run(self, ctx: GateContext) -> GateResult:
        cfg = {**_DEFAULTS, **ctx.config.get("architecture", {})}
        root = ctx.repo_root
        pkg_root = root / cfg["package_root"]
        findings: list[str] = []

        py_files = sorted(pkg_root.rglob("*.py"))
        import_graph: dict[str, set[str]] = {}

        for path in py_files:
            rel = path.relative_to(root).as_posix()
            try:
                source = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            lines = source.count("\n") + 1
            if lines > cfg["file_max_lines"]:
                findings.append(f"{rel}: {lines} lines exceeds budget {cfg['file_max_lines']}")
            try:
                tree = ast.parse(source)
            except SyntaxError as error:
                findings.append(f"{rel}: syntax error: {error}")
                continue

            findings.extend(self._func_budget(tree, rel, cfg["func_max_lines"]))
            module = self._module_name(path, root, cfg["package_root"])
            imports = self._imports(tree)
            import_graph[module] = imports
            if "gates" in module.split(".") and module.rsplit(".", 1)[-1] != "base":
                for imp in imports:
                    if imp.startswith("selfproof.core") or imp.startswith("selfproof.cli"):
                        findings.append(f"{rel}: layering: gate imports {imp}")

        findings.extend(self._cycles(import_graph))
        findings.extend(self._dependency_adrs(root))

        if findings:
            return GateResult(
                self.name, Verdict.FAIL, f"{len(findings)} architecture finding(s)",
                output="\n".join(findings), details={"findings": findings},
            )
        return GateResult(self.name, Verdict.PASS, "layering, cycles, budgets and deps clean")

    @staticmethod
    def _module_name(path: Path, root: Path, pkg_root: str) -> str:
        rel = path.relative_to(root / pkg_root).with_suffix("")
        parts = [p for p in rel.parts if p != "__init__"]
        return ".".join(["selfproof", *parts]) if parts else "selfproof"

    @staticmethod
    def _imports(tree: ast.AST) -> set[str]:
        names: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                names.add(node.module)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    names.add(alias.name)
        return {n for n in names if n.startswith("selfproof")}

    @staticmethod
    def _func_budget(tree: ast.AST, rel: str, budget: int) -> list[str]:
        out: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                end = getattr(node, "end_lineno", node.lineno)
                length = end - node.lineno + 1
                if length > budget:
                    out.append(
                        f"{rel}:{node.lineno}: function '{node.name}' is "
                        f"{length} lines (budget {budget})"
                    )
        return out

    @staticmethod
    def _cycles(graph: dict[str, set[str]]) -> list[str]:
        visiting: set[str] = set()
        done: set[str] = set()
        out: list[str] = []

        def visit(node: str, stack: list[str]) -> None:
            if node in done:
                return
            if node in visiting:
                out.append("import cycle: " + " -> ".join(stack + [node]))
                return
            visiting.add(node)
            for dep in graph.get(node, set()):
                if dep in graph:
                    visit(dep, stack + [node])
            visiting.discard(node)
            done.add(node)

        for module in graph:
            visit(module, [])
        return out

    @staticmethod
    def _dependency_adrs(root: Path) -> list[str]:
        pyproject = root / "pyproject.toml"
        if not pyproject.exists():
            return []
        with open(pyproject, "rb") as handle:
            data = tomllib.load(handle)
        deps = data.get("project", {}).get("dependencies", [])
        if not deps:
            return []
        adr_text = " ".join(
            p.read_text(encoding="utf-8", errors="ignore")
            for p in (root / "docs" / "decisions").glob("*.md")
        )
        out: list[str] = []
        for dep in deps:
            name = dep.split("[")[0].split(">")[0].split("=")[0].split("<")[0].strip()
            if name and name not in adr_text:
                out.append(f"dependency '{name}' has no ADR line under docs/decisions/")
        return out
