"""Fleet mode: enumerate and classify the owner's repositories (concept 9, 15).

Read-only. It lists the repositories of both accounts through the ``gh`` CLI and
classifies each as in write-scope (the two charter repositories) or read-only.
It does not clone or run gates across other repositories yet, and it invents no
findings: a finding counts as "improved" only with a recorded before entry, a
fix commit and an after entry, none of which exist across the fleet yet. That
limit is stated in the report.
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from ..gates.base import run_command

IN_SCOPE = ("renker-industries/selfproof", "renker-industries/selfproof-holdout")


@dataclass(frozen=True)
class FleetRepo:
    """One repository as seen by fleet mode."""

    full_name: str
    visibility: str
    language: str
    in_scope: bool


@dataclass(frozen=True)
class FleetSnapshot:
    """The result of a fleet scan across accounts."""

    repos: list[FleetRepo]
    errors: list[str] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.repos)

    @property
    def by_visibility(self) -> dict[str, int]:
        return dict(Counter(r.visibility for r in self.repos))

    @property
    def by_language(self) -> dict[str, int]:
        return dict(Counter(r.language for r in self.repos))

    @property
    def in_scope(self) -> list[FleetRepo]:
        return [r for r in self.repos if r.in_scope]


def parse_repo_list(account: str, json_text: str) -> list[FleetRepo]:
    """Parse ``gh repo list --json`` output into :class:`FleetRepo` objects."""
    repos: list[FleetRepo] = []
    for item in json.loads(json_text):
        full = f"{account}/{item['name']}"
        lang = (item.get("primaryLanguage") or {}).get("name") or "none"
        repos.append(
            FleetRepo(
                full_name=full,
                visibility=str(item.get("visibility", "UNKNOWN")).lower(),
                language=lang,
                in_scope=full in IN_SCOPE,
            )
        )
    return repos


def list_repos(account: str, limit: int = 200) -> tuple[list[FleetRepo], str | None]:
    """List an account's repositories via ``gh``. Returns ``(repos, error)``."""
    code, out = run_command(
        ["gh", "repo", "list", account, "--limit", str(limit),
         "--json", "name,visibility,primaryLanguage"],
        cwd=Path.cwd(),
        timeout=60,
    )
    if code is None:
        return [], f"{account}: gh not available or timed out"
    if code != 0:
        return [], f"{account}: gh repo list failed"
    try:
        return parse_repo_list(account, out), None
    except (ValueError, KeyError) as error:
        return [], f"{account}: cannot parse gh output: {error}"


def scan(accounts: list[str]) -> FleetSnapshot:
    """Scan every account and return a combined snapshot."""
    repos: list[FleetRepo] = []
    errors: list[str] = []
    for account in accounts:
        found, error = list_repos(account)
        repos.extend(found)
        if error:
            errors.append(error)
    return FleetSnapshot(repos=sorted(repos, key=lambda r: r.full_name), errors=errors)


def report(snapshot: FleetSnapshot) -> str:
    """Render an honest fleet summary."""
    lines = [
        "SELFPROOF FLEET",
        f"  repositories seen : {snapshot.total}",
        f"  by visibility     : {snapshot.by_visibility}",
        f"  in write-scope    : {len(snapshot.in_scope)} (charter repos only)",
        "  note: other repositories are read-only; cross-repo gate scanning and",
        "        before/after 'improved' tracking are not implemented yet.",
    ]
    for error in snapshot.errors:
        lines.append(f"  error: {error}")
    return "\n".join(lines)
