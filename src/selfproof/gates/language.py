"""The ``language`` gate: enforce the English-only rule (concept 10.1, W12).

This is a dependency-free heuristic, not a language classifier. It flags a text
file when it contains German-specific letters or several common German
stopwords. The markers themselves are loaded from ``data/german_markers.json``
(data, not prose), which is excluded from the scan so the detector does not flag
itself. The deliberate non-English fixtures under
``tests/fixtures/non_english/`` and the imported kernel are excluded via config.

Known limitation (stated in the gate reference): proper names or quoted German
inside otherwise-English text can be false positives; suppress them with a
reason and expiry. It will not catch non-English languages without their own
markers. It is a floor, not a proof of good English.
"""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

from .base import Gate, GateContext, GateResult, Verdict, run_command

_WORD_RE = re.compile(r"\w+", re.UNICODE)
_STOPWORD_THRESHOLD = 3


@lru_cache(maxsize=1)
def _markers() -> tuple[frozenset, frozenset]:
    """Load and cache the German character and stopword marker sets."""
    path = Path(__file__).parent / "data" / "german_markers.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    return frozenset(data["chars"]), frozenset(data["stopwords"])


class LanguageGate(Gate):
    """Flag files that look like they contain German text."""

    name = "language"

    def run(self, ctx: GateContext) -> GateResult:
        exclude = tuple(ctx.config["language"]["exclude"])
        suffixes = tuple(ctx.config["language"]["text_suffixes"])

        code, out = run_command(["git", "ls-files"], ctx.repo_root)
        if code is None:
            return GateResult(
                self.name, Verdict.ERROR,
                "cannot list tracked files (git missing?)",
                command="git ls-files", exit_code=code, output=out,
            )
        if code != 0:
            return GateResult(
                self.name, Verdict.ERROR, "git ls-files failed",
                command="git ls-files", exit_code=code, output=out,
            )

        findings: dict[str, list[int]] = {}
        for rel in out.splitlines():
            rel = rel.strip()
            if not rel or not rel.endswith(suffixes):
                continue
            if any(rel.startswith(prefix) for prefix in exclude):
                continue
            path = ctx.repo_root / rel
            if not path.exists():
                continue
            lines = self._german_lines(path)
            if lines:
                findings[rel] = lines

        if findings:
            listing = "\n".join(f"  {f}: lines {ln}" for f, ln in sorted(findings.items()))
            return GateResult(
                self.name, Verdict.FAIL,
                f"non-English text in {len(findings)} file(s)",
                output=listing, details={"files": findings},
            )
        return GateResult(
            self.name, Verdict.PASS, "all scanned text files look English",
            details={"excludes": list(exclude)},
        )

    @staticmethod
    def _german_lines(path: Path) -> list[int]:
        """Return 1-based line numbers that look German, or an empty list."""
        chars, stopwords = _markers()
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            return []
        hits: list[int] = []
        for i, line in enumerate(text.splitlines(), start=1):
            if any(ch in chars for ch in line):
                hits.append(i)
                continue
            words = {w.lower() for w in _WORD_RE.findall(line)}
            if len(words & stopwords) >= _STOPWORD_THRESHOLD:
                hits.append(i)
        return hits
