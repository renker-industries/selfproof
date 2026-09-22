"""Release-readiness check and a minimal SBOM (concept sections 11, 12).

The readiness check refuses to call a build release-ready unless every required
gate passes with no ``SKIPPED``, the ledger verifies, the generated rules files
are current, and the required top-level files exist. It reports problems plainly
rather than asserting readiness it cannot back up.
"""

from __future__ import annotations

from pathlib import Path

from . import __version__
from .core.ledger import Ledger, LedgerError
from .core.rules import check_generated
from .core.runner import run_gates

_REQUIRED_FILES = ("LICENSE", "NOTICE", "SECURITY.md", "README.md", "CHANGELOG.md")


def readiness(repo_root: str | Path) -> list[str]:
    """Return a list of readiness problems; empty means release-ready."""
    root = Path(repo_root)
    problems: list[str] = []

    report = run_gates(root)
    for result in report.results:
        if result.verdict.value != "PASS":
            problems.append(f"gate {result.gate}: {result.verdict.value} (must be PASS)")

    try:
        Ledger(root / "docs" / "reports" / "ledger.jsonl").verify()
    except LedgerError as error:
        problems.append(f"ledger: {error}")

    for drift in check_generated(root):
        problems.append(f"rules: {drift}")

    for name in _REQUIRED_FILES:
        if not (root / name).exists():
            problems.append(f"missing required file: {name}")

    return problems


def sbom(repo_root: str | Path) -> dict:
    """Return a minimal CycloneDX-style SBOM for the project (zero runtime deps)."""
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "metadata": {
            "component": {
                "type": "application", "name": "selfproof", "version": __version__,
            }
        },
        "components": [
            {"type": "library", "name": "renker-core", "scope": "required",
             "description": "Imported decision kernel; zero runtime dependencies."},
        ],
        "note": "Selfproof has zero third-party runtime dependencies; external "
                "tools are orchestrated, never bundled.",
    }
