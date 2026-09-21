"""The ``test_weakening`` gate: block changes that quietly weaken the checks.

Diff-based (concept 2.3, 5). Compared against the merge-base with ``main``, it
flags:

- removed assertions (``assert`` lines deleted);
- removed tests (``def test_...`` deleted);
- added skip/xfail markers (``@pytest.mark.skip``, ``pytest.skip(``,
  ``@pytest.mark.xfail``).

If no comparison base is available (a fresh repo, or ``main`` cannot be
resolved), the gate returns ``PASS`` because there is nothing to compare. A
finding here means the change is Tier B and needs a signed approval; the gate
itself never merges anything.

Known limitation: "loosened thresholds" cannot be detected generically and are
left to review; this is stated in the gate reference.
"""

from __future__ import annotations

from .base import Gate, GateContext, GateResult, Verdict, run_command

# A skip marker counts only when the added line *is* the decorator/call, not when
# it merely mentions the marker in a string, tuple or docstring.
_SKIP_PREFIXES = (
    "@pytest.mark.skip",
    "@pytest.mark.xfail",
    "@unittest.skip",
    "pytest.skip(",
    "self.skipTest(",
)


class TestWeakeningGate(Gate):
    """Flag deleted tests/assertions and added skip markers in the diff."""

    name = "test_weakening"

    def run(self, ctx: GateContext) -> GateResult:
        base = self._base(ctx)
        if base is None:
            return GateResult(
                self.name, Verdict.PASS, "no comparison base; nothing to weaken",
            )
        code, diff = run_command(
            ["git", "diff", "--unified=0", f"{base}...HEAD", "--", "*.py"], ctx.repo_root
        )
        if code is None or code != 0:
            return GateResult(
                self.name, Verdict.PASS, f"cannot diff against {base}; skipping comparison",
                output=diff,
            )

        findings: list[str] = []
        for line in diff.splitlines():
            if line.startswith("---") or line.startswith("+++"):
                continue
            if line.startswith("-"):
                body = line[1:].strip()
                if body.startswith("assert ") or body.startswith("assert("):
                    findings.append(f"removed assertion: {body[:70]}")
                elif body.startswith("def test_"):
                    findings.append(f"removed test: {body[:70]}")
            elif line.startswith("+"):
                body = line[1:].strip()
                if body.startswith(_SKIP_PREFIXES):
                    findings.append(f"added skip/xfail marker: {body[:70]}")

        if findings:
            return GateResult(
                self.name, Verdict.FAIL,
                f"{len(findings)} weakening change(s) need approval",
                command=f"git diff {base}...HEAD", output="\n".join(findings),
                details={"findings": findings, "base": base},
            )
        return GateResult(
            self.name, Verdict.PASS, f"no test weakening against {base}",
            command=f"git diff {base}...HEAD",
        )

    @staticmethod
    def _base(ctx: GateContext) -> str | None:
        for ref in ("origin/main", "main"):
            code, out = run_command(["git", "merge-base", ref, "HEAD"], ctx.repo_root)
            if code == 0 and out.strip():
                sha = out.strip()
                # If HEAD == base (we ARE main), there is nothing new to compare.
                head_code, head = run_command(["git", "rev-parse", "HEAD"], ctx.repo_root)
                if head_code == 0 and head.strip() == sha:
                    return None
                return sha
        return None
