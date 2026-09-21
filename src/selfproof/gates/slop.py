"""The ``slop`` gate: catch typical AI-generated slop in shipped code.

Dependency-free AST + text heuristics over the Selfproof source and tests
(the imported kernel is excluded). It flags:

- placeholder bodies: a function/class whose body is only ``...`` (Ellipsis),
  outside ``typing.Protocol`` / ``@overload`` where an ellipsis is idiomatic;
- placeholder markers in shipped code: ``TODO``, ``FIXME``, ``XXX``, ``HACK``;
- over-broad exception handling: ``except:`` or ``except Exception`` whose body
  is only ``pass`` (silently swallowed errors);
- tests without assertions: a ``test_*`` function with no ``assert`` and no
  ``pytest.raises`` / ``self.assert*`` call.

Deliberately NOT flagged: ``raise NotImplementedError`` (a legitimate abstract
method). Dead-code and copy-paste detection are deferred to external tools
(vulture, jscpd) in a later ADR; this gate states that limit in its reference.
"""

from __future__ import annotations

import ast
from pathlib import Path

from .base import Gate, GateContext, GateResult, Verdict, run_command

_MARKERS = ("TODO", "FIXME", "XXX", "HACK")


class SlopGate(Gate):
    """Flag AI slop in shipped Python files."""

    name = "slop"

    def run(self, ctx: GateContext) -> GateResult:
        exclude = tuple(ctx.config.get("slop", {}).get("exclude", [
            "src/renker_core/", "tests/corpus/bad/", "tests/fixtures/",
        ]))
        code, out = run_command(["git", "ls-files", "*.py"], ctx.repo_root)
        if code is None or code != 0:
            return GateResult(
                self.name, Verdict.ERROR, "cannot list python files",
                command="git ls-files *.py", exit_code=code, output=out,
            )

        findings: list[str] = []
        for rel in out.splitlines():
            rel = rel.strip()
            if not rel or any(rel.startswith(p) for p in exclude):
                continue
            findings.extend(self._scan(ctx.repo_root / rel, rel))

        if findings:
            return GateResult(
                self.name, Verdict.FAIL,
                f"{len(findings)} slop finding(s)",
                output="\n".join(findings), details={"findings": findings},
            )
        return GateResult(self.name, Verdict.PASS, "no slop detected")

    def _scan(self, path: Path, rel: str) -> list[str]:
        try:
            source = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return []
        out: list[str] = []

        for i, line in enumerate(source.splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith("#") and any(m in stripped for m in _MARKERS):
                out.append(f"{rel}:{i}: placeholder marker in comment: {stripped[:60]}")

        try:
            tree = ast.parse(source)
        except SyntaxError as error:
            return out + [f"{rel}: syntax error: {error}"]

        out.extend(self._ast_findings(tree, rel))
        return out

    def _ast_findings(self, tree: ast.AST, rel: str) -> list[str]:
        out: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                broad = node.type is None or (
                    isinstance(node.type, ast.Name) and node.type.id == "Exception"
                )
                only_pass = len(node.body) == 1 and isinstance(node.body[0], ast.Pass)
                if broad and only_pass:
                    out.append(f"{rel}:{node.lineno}: broad except swallows errors with pass")
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                if not self._has_assertion(node):
                    out.append(f"{rel}:{node.lineno}: test '{node.name}' has no assertion")
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if self._is_ellipsis_only(node) and not self._is_protocol_ok(node):
                    out.append(f"{rel}:{node.lineno}: '{node.name}' is a '...' placeholder")
        return out

    @staticmethod
    def _has_assertion(node: ast.FunctionDef) -> bool:
        for n in ast.walk(node):
            if isinstance(n, ast.Assert):
                return True
            if isinstance(n, ast.Attribute) and n.attr.startswith("assert"):
                return True
            if isinstance(n, ast.Call):
                func = n.func
                if isinstance(func, ast.Attribute) and func.attr in ("raises", "warns"):
                    return True
        return False

    @staticmethod
    def _is_ellipsis_only(node: ast.AST) -> bool:
        def is_docstring(stmt: ast.stmt) -> bool:
            return (
                isinstance(stmt, ast.Expr)
                and isinstance(stmt.value, ast.Constant)
                and isinstance(stmt.value.value, str)
            )

        body = [b for b in getattr(node, "body", []) if not is_docstring(b)]
        if len(body) != 1 or not isinstance(body[0], ast.Expr):
            return False
        value = body[0].value
        return isinstance(value, ast.Constant) and value.value is Ellipsis

    @staticmethod
    def _is_protocol_ok(node: ast.AST) -> bool:
        # An ellipsis body is fine for Protocol methods and @overload / @abstractmethod.
        decorators = getattr(node, "decorator_list", [])
        for dec in decorators:
            name = dec.id if isinstance(dec, ast.Name) else getattr(dec, "attr", "")
            if name in ("overload", "abstractmethod"):
                return True
        return False
