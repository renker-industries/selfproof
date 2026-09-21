"""The ``docs_coverage`` gate: presence and freshness of documentation.

Leaf gate (filesystem + ``ast`` only). It checks a defensible subset of the
documentation requirement matrix (concept 10.2):

- every ``.py`` under ``src/selfproof`` has a module docstring;
- every public top-level function and class has a docstring;
- every directory under ``src/selfproof`` has a ``README.md``;
- every gate class under ``src/selfproof/gates`` has a reference page at
  ``docs/reference/gates/<name>.md``;
- a generated CLI reference exists at ``docs/reference/cli.md``.

Honest limit: it measures presence and structure, not quality. Docstring
coverage is checked for modules, public top-level functions and public classes
(methods are covered by their class). This limit is stated in the reference.
"""

from __future__ import annotations

import ast
from pathlib import Path

from .base import Gate, GateContext, GateResult, Verdict

_PKG = "src/selfproof"


class DocsCoverageGate(Gate):
    """Check that required documentation exists and is structurally complete."""

    name = "docs_coverage"

    def run(self, ctx: GateContext) -> GateResult:
        root = ctx.repo_root
        pkg = root / _PKG
        findings: list[str] = []

        findings.extend(self._docstrings(pkg, root))
        findings.extend(self._dir_readmes(pkg, root))
        findings.extend(self._gate_refs(pkg, root))
        if not (root / "docs" / "reference" / "cli.md").exists():
            findings.append("missing generated CLI reference: docs/reference/cli.md")

        if findings:
            return GateResult(
                self.name, Verdict.FAIL, f"{len(findings)} documentation gap(s)",
                output="\n".join(findings), details={"findings": findings},
            )
        return GateResult(self.name, Verdict.PASS, "required documentation present")

    def _docstrings(self, pkg: Path, root: Path) -> list[str]:
        out: list[str] = []
        for path in sorted(pkg.rglob("*.py")):
            rel = path.relative_to(root).as_posix()
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError, SyntaxError) as error:
                out.append(f"{rel}: cannot parse: {error}")
                continue
            if ast.get_docstring(tree) is None:
                out.append(f"{rel}: missing module docstring")
            for node in tree.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    if not node.name.startswith("_") and ast.get_docstring(node) is None:
                        out.append(f"{rel}:{node.lineno}: public '{node.name}' has no docstring")
        return out

    @staticmethod
    def _dir_readmes(pkg: Path, root: Path) -> list[str]:
        out: list[str] = []
        for directory in sorted({p.parent for p in pkg.rglob("*.py")}):
            if directory.name == "data":
                continue  # data directories hold assets, not modules
            if not (directory / "README.md").exists():
                out.append(f"{directory.relative_to(root).as_posix()}: missing README.md")
        return out

    @staticmethod
    def _gate_refs(pkg: Path, root: Path) -> list[str]:
        out: list[str] = []
        gates_dir = pkg / "gates"
        for path in sorted(gates_dir.glob("*.py")):
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError, SyntaxError):
                continue
            for node in ast.walk(tree):
                if not isinstance(node, ast.ClassDef) or node.name == "Gate":
                    continue
                gate_name = DocsCoverageGate._class_name_attr(node)
                if gate_name is None:
                    continue
                ref = root / "docs" / "reference" / "gates" / f"{gate_name}.md"
                if not ref.exists():
                    rel_ref = ref.relative_to(root).as_posix()
                    out.append(f"gate '{gate_name}' has no reference at {rel_ref}")
        return out

    @staticmethod
    def _class_name_attr(node: ast.ClassDef) -> str | None:
        """Return the string value of a class-level ``name = "..."`` assignment."""
        for stmt in node.body:
            target = None
            if isinstance(stmt, ast.Assign) and stmt.targets:
                target = stmt.targets[0]
            elif isinstance(stmt, ast.AnnAssign):
                target = stmt.target
            if isinstance(target, ast.Name) and target.id == "name":
                value = getattr(stmt, "value", None)
                if isinstance(value, ast.Constant) and isinstance(value.value, str):
                    return value.value
        return None
