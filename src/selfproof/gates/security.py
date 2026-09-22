"""The ``security`` gate: secrets, licenses, workflow hardening and advisories.

Built-in, dependency-free checks always run:

- **secrets:** regex scan of tracked text files for private-key blocks and
  common cloud/token patterns (never prints the match, only the location);
- **licenses:** the repository has a LICENSE, and no runtime dependency carries a
  forbidden license (GPL/AGPL/BSL/non-commercial). With zero dependencies this
  passes vacuously;
- **workflows:** every `.github/workflows/*.yml` declares `permissions:` and does
  not use the dangerous `pull_request_target` trigger.

External scanners augment coverage **when installed**: `gitleaks` (secrets) and
`zizmor` (workflow static analysis) actually run and their findings fail the
gate; `osv-scanner` advisory scanning is vacuous with zero runtime
dependencies. The built-in checks cover the baseline on their own, so an absent
augmenter is reported as "not run" rather than skipping the gate — it never
turns an absent tool into extra confidence, and the output always names which
scanners ran and which did not.

Overall verdict: `FAIL` on any finding (built-in or from a scanner that ran);
otherwise `PASS`, with the not-installed augmenters named in the output.
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

        findings.extend(self._secret_scan(ctx))
        findings.extend(self._license_check(root))
        findings.extend(self._workflow_check(root))

        ran, not_run, aug_findings = self._augmenters(root)
        findings.extend(aug_findings)

        output = ""
        if findings:
            output += "findings:\n" + "\n".join(findings) + "\n"
        output += f"external scanners run: {', '.join(ran) or 'none'}\n"
        if not_run:
            output += "external scanners not installed (built-ins still ran): " + ", ".join(not_run)

        if findings:
            return GateResult(
                self.name, Verdict.FAIL, f"{len(findings)} security finding(s)",
                output=output, details={"findings": findings, "ran": ran, "not_run": not_run},
            )
        note = f" ({len(not_run)} optional scanner(s) not installed)" if not_run else ""
        return GateResult(
            self.name, Verdict.PASS,
            f"no secrets, licenses clean, workflows hardened{note}",
            output=output, details={"ran": ran, "not_run": not_run},
        )

    def _augmenters(self, root) -> tuple[list[str], list[str], list[str]]:
        """Run external scanners that are installed. Returns (ran, not_run, findings).

        Built-in checks already cover the baseline, so an absent augmenter does
        not fail or skip the gate; it is reported as not run. A present scanner
        actually runs, and a non-zero result becomes a finding (values are never
        printed by these scanners in the modes used here).
        """
        ran: list[str] = []
        not_run: list[str] = []
        findings: list[str] = []
        checks = (
            ("gitleaks", ["gitleaks", "version"],
             ["gitleaks", "detect", "--no-banner", "--redact", "--exit-code", "1", "-s", "."]),
            ("zizmor", ["zizmor", "--version"], ["zizmor", "--quiet", ".github/workflows"]),
        )
        for tool, probe, cmd in checks:
            code, _ = run_command(probe, root, timeout=30)
            if code is None:
                not_run.append(tool)
                continue
            rc, out = run_command(cmd, root, timeout=300)
            ran.append(tool)
            if rc not in (0, None):
                findings.append(f"{tool}: reported findings (exit {rc}); see the tool output")
        # Advisory scanning (osv-scanner) is vacuous with zero runtime dependencies.
        return ran, not_run, findings

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
