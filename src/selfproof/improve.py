"""The improvement engine: measure, compare, ratchet (concept section 2.6).

This is the honest core of ``selfproof improve``. It measures real, cheap
metrics about the repository, compares them to a ratchet baseline, and refuses
to move the baseline when a tracked metric regresses. It does not fabricate
improvements, and it states its own limit: the hidden-holdout cycles that
resist overfitting need a holdout populated by a session that is not the
builder, which is an owner step (see ``OWNER_TODO.md``).

Tracked metrics and their good direction:

- ``gates`` (up or flat), ``adapters`` (up or flat), ``test_functions``
  (up or flat), ``corpus_bad`` / ``corpus_good`` (up or flat),
  ``runtime_dependencies`` (down or flat). ``src_lines`` is reported but not a
  regression on growth, because new capability legitimately adds code.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

from .adapters import ADAPTERS
from .gates import GATES

_BASELINE = "docs/reports/ratchet-baseline.json"
# name -> True means "higher is better", False means "lower is better".
_DIRECTION = {
    "gates": True, "adapters": True, "test_functions": True,
    "corpus_bad": True, "corpus_good": True, "runtime_dependencies": False,
}


def measure(repo_root: str | Path) -> dict:
    """Compute the tracked metrics for the repository at ``repo_root``."""
    root = Path(repo_root)
    tests = root / "tests"
    return {
        "gates": len(GATES),
        "adapters": len(ADAPTERS),
        "test_functions": _count_test_functions(tests),
        "corpus_bad": _count_files(root / "tests" / "corpus" / "bad"),
        "corpus_good": _count_files(root / "tests" / "corpus" / "good"),
        "runtime_dependencies": 0,
        "src_lines": _count_lines(root / "src" / "selfproof"),
    }


def load_baseline(repo_root: str | Path) -> dict | None:
    """Return the ratchet baseline metrics, or ``None`` if none exists."""
    path = Path(repo_root) / _BASELINE
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8")).get("metrics")


def regressions(baseline: dict, current: dict) -> list[str]:
    """Return tracked metrics that regressed against the baseline."""
    out: list[str] = []
    for name, higher_better in _DIRECTION.items():
        before = baseline.get(name)
        after = current.get(name)
        if before is None or after is None:
            continue
        if (higher_better and after < before) or (not higher_better and after > before):
            out.append(f"{name}: {before} -> {after}")
    return out


def ratchet(repo_root: str | Path) -> tuple[bool, list[str]]:
    """Move the baseline to the current metrics unless something regressed.

    Returns ``(moved, problems)``. ``moved`` is False when a regression blocks
    the update or when there is no change to record.
    """
    root = Path(repo_root)
    current = measure(root)
    baseline = load_baseline(root)
    if baseline is not None:
        problems = regressions(baseline, current)
        if problems:
            return False, problems
        if baseline == {k: current[k] for k in baseline}:
            return False, ["no change since the baseline"]
    path = root / _BASELINE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"metrics": current}, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return True, []


def _count_test_functions(tests: Path) -> int:
    if not tests.exists():
        return 0
    total = 0
    for path in tests.rglob("test_*.py"):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, SyntaxError):
            continue
        total += sum(
            1 for n in ast.walk(tree)
            if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")
        )
    return total


def _count_files(directory: Path) -> int:
    return sum(1 for p in directory.rglob("*") if p.is_file()) if directory.exists() else 0


def _count_lines(directory: Path) -> int:
    if not directory.exists():
        return 0
    return sum(
        p.read_text(encoding="utf-8", errors="ignore").count("\n") + 1
        for p in directory.rglob("*.py")
    )
