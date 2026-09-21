"""The ``docs_claims`` gate: keep user-facing claims honest.

Leaf gate (text only). Over the user-facing docs (README and the published
``docs/wiki``, ``docs/guides``, ``docs/explanation`` trees), it flags:

- forbidden absolute claims (e.g. "unhackable", "100% secure", "bug-free"),
  unless the line negates them (a disclaimer such as "does not promise
  'unhackable'" is allowed);
- a bare percentage or "percent" not accompanied on the line by an evidence
  label (`planned`, `estimated`, `measured`, `example`, `net`, `benchmark`).

Internal records (`docs/CONCEPT.md`, `docs/decisions/`, `docs/reports/`) are not
scanned: they discuss numbers and phrases as labelled analysis, not as product
claims. Executing `verify`-tagged code blocks in a sandbox is a planned
extension, stated in the reference.
"""

from __future__ import annotations

import re
from pathlib import Path

from .base import Gate, GateContext, GateResult, Verdict

_FORBIDDEN = (
    "unhackable", "100% secure", "absolutely secure", "completely secure",
    "bug-free", "bug free", "no bugs", "zero bugs", "guaranteed secure",
    "perfectly secure", "totally secure",
)
_NEGATIONS = ("not", "never", "no ", "cannot", "can't", "don't", "does not",
              "doesn't", "without", "avoid", "instead of")
_LABELS = ("planned", "estimated", "measured", "example", "net", "benchmark",
           "sample size")
_PERCENT_RE = re.compile(r"(\d+(\.\d+)?\s?%|\d+\s?percent)", re.IGNORECASE)
_SCOPE = ("README.md", "docs/wiki", "docs/guides", "docs/explanation")


class DocsClaimsGate(Gate):
    """Flag unsupported or absolute claims in user-facing documentation."""

    name = "docs_claims"

    def run(self, ctx: GateContext) -> GateResult:
        root = ctx.repo_root
        findings: list[str] = []
        for rel in self._scoped_files(root):
            path = root / rel
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            findings.extend(self._scan(text, rel))

        if findings:
            return GateResult(
                self.name, Verdict.FAIL, f"{len(findings)} claim issue(s)",
                output="\n".join(findings), details={"findings": findings},
            )
        return GateResult(self.name, Verdict.PASS, "user-facing claims are labelled or negated")

    @staticmethod
    def _scoped_files(root: Path) -> list[str]:
        files: list[str] = []
        readme = root / "README.md"
        if readme.exists():
            files.append("README.md")
        for sub in ("docs/wiki", "docs/guides", "docs/explanation"):
            base = root / sub
            if base.exists():
                files.extend(p.relative_to(root).as_posix() for p in base.rglob("*.md"))
        return files

    def _scan(self, text: str, rel: str) -> list[str]:
        out: list[str] = []
        for i, line in enumerate(text.splitlines(), start=1):
            low = line.lower()
            negated = any(neg in low for neg in _NEGATIONS)
            for phrase in _FORBIDDEN:
                if phrase in low and not negated:
                    out.append(
                        f"{rel}:{i}: forbidden absolute claim '{phrase}': {line.strip()[:60]}"
                    )
            if self._has_percent(line) and not any(lbl in low for lbl in _LABELS):
                out.append(f"{rel}:{i}: unlabelled number/percentage: {line.strip()[:70]}")
        return out

    @staticmethod
    def _has_percent(line: str) -> bool:
        return bool(_PERCENT_RE.search(line))
