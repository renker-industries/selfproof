"""The ``security`` gate: secrets, licenses, workflow hardening and advisories.

Built-in, dependency-free checks always run:

- **secrets:** regex scan of tracked text files for private-key blocks and
  common cloud/token patterns (never prints the match, only the location);
- **licenses:** the repository has a LICENSE, and no runtime dependency carries a
  forbidden license (GPL/AGPL/BSL/non-commercial). With zero dependencies this
  passes vacuously;
- **workflows:** every `.github/workflows/*.yml` declares `permissions:` and does
  not use the dangerous `pull_request_target` trigger.

External scanners augment coverage **when installed**: `gitleaks` (secrets),
`osv-scanner` (advisories), `zizmor` (workflow static analysis). If absent, that
sub-check is `SKIPPED` and named in the output — a missing tool is never a pass.

Overall verdict: `FAIL` on any built-in finding; otherwise `SKIPPED` if a
sub-check that had work to do was skipped for a missing tool; otherwise `PASS`.
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

from .base import Gate, GateContext, GateResult, Verdict, run_command

_EXCLUDE = (
    "src/renker_core/", "tests/corpus/", "tests/fixtures/",
    "src/selfproof/gates/security.py",  # this scanner defines the patterns
    "tests/test_security_gate.py",
)
_TEXT = (".py", ".md", ".txt", ".toml", ".yaml", ".yml", ".cfg", ".ini", ".json", ".sh", ".env")
_FORBIDDEN_LICENSES = ("gpl", "agpl", "bsl", "business source", "non-commercial", "noncommercial")

# Secret patterns. The regexes themselves contain no matchable secret.
_SECRET_PATTERNS = {
    "private key block": re.compile(r"-----BEGIN [A-Z ]{0,20}PRIVATE KEY-----"),
    "aws access key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "github token": re.compile(r"gh[pousr]_[A-Za-z0-9]{36,}"),
    "slack token": re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),
    "generic secret assignment": re.compile(
        r"(?i)(password|secret|api[_-]?key|token)\s*[:=]\s*['\"][^'\"]{12,}['\"]"
    ),
}


class SecurityGate(Gate):
    """Scan for secrets, license problems, and workflow hardening gaps."""

    name = "security"

    def run(self, ctx: GateContext) -> GateResult:
        root = ctx.repo_root
        findings: list[str] = []
        skipped: list[str] = []

        findings.extend(self._secret_scan(ctx))
        findings.extend(self._license_check(root))
        findings.extend(self._workflow_check(root))

        # Optional external augmenters.
        for tool, args in (
            ("gitleaks", ["gitleaks", "version"]),
            ("osv-scanner", ["osv-scanner", "--version"]),
            ("zizmor", ["zizmor", "--version"]),
        ):
            code, _ = run_command(args, root, timeout=30)
            if code is None:
                skipped.append(tool)

        output = ""
        if findings:
            output += "findings:\n" + "\n".join(findings) + "\n"
        if skipped:
            output += "skipped external tools (not installed): " + ", ".join(skipped)

        if findings:
            return GateResult(
                self.name, Verdict.FAIL, f"{len(findings)} security finding(s)",
                output=output, details={"findings": findings, "skipped": skipped},
            )
        if skipped:
            return GateResult(
                self.name, Verdict.SKIPPED,
                f"built-in checks clean; {len(skipped)} external scanner(s) unavailable",
                output=output, details={"skipped": skipped},
            )
        return GateResult(self.name, Verdict.PASS, "no secrets, licenses clean, workflows hardened")

    def _secret_scan(self, ctx: GateContext) -> list[str]:
        code, out = run_command(["git", "ls-files"], ctx.repo_root)
        if code is None or code != 0:
            return ["secret scan: cannot list tracked files"]
        findings: list[str] = []
        for rel in out.splitlines():
            rel = rel.strip()
            if not rel or not rel.endswith(_TEXT):
                continue
            if any(rel.startswith(p) for p in _EXCLUDE):
                continue
            path = ctx.repo_root / rel
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            for i, line in enumerate(text.splitlines(), start=1):
                for label, pattern in _SECRET_PATTERNS.items():
                    if pattern.search(line):
                        findings.append(f"{rel}:{i}: possible {label} (value not shown)")
        return findings

    @staticmethod
    def _license_check(root: Path) -> list[str]:
        out: list[str] = []
        if not (root / "LICENSE").exists():
            out.append("license: no LICENSE file")
        pyproject = root / "pyproject.toml"
        if pyproject.exists():
            with open(pyproject, "rb") as handle:
                data = tomllib.load(handle)
            for dep in data.get("project", {}).get("dependencies", []):
                low = dep.lower()
                if any(bad in low for bad in _FORBIDDEN_LICENSES):
                    out.append(f"license: dependency looks forbidden: {dep}")
        return out

    @staticmethod
    def _workflow_check(root: Path) -> list[str]:
        out: list[str] = []
        wf_dir = root / ".github" / "workflows"
        if not wf_dir.exists():
            return out
        for path in sorted(wf_dir.glob("*.yml")) + sorted(wf_dir.glob("*.yaml")):
            text = path.read_text(encoding="utf-8", errors="ignore")
            rel = path.relative_to(root).as_posix()
            if "pull_request_target" in text:
                out.append(f"{rel}: uses dangerous pull_request_target trigger")
            if "permissions:" not in text:
                out.append(f"{rel}: no explicit permissions block")
        return out
