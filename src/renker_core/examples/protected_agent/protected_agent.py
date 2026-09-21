from __future__ import annotations

import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from renker_core import (
    Actor,
    Capability,
    CapabilityStore,
    Decision,
    GuardedFilesystem,
    PathScope,
)
from renker_core.audit import AuditLog


def build_guard(workdir: Path) -> tuple[GuardedFilesystem, AuditLog, Actor]:
    now = datetime.now(timezone.utc)
    agent = Actor("agent", "demo-session")
    owner = Actor("human", "owner")

    store = CapabilityStore()
    store.grant(
        Capability(
            capability="filesystem.read",
            scope=PathScope(base=str(workdir / "project")),
            granted_to=agent.urn,
            granted_by=owner.urn,
            issued_at=now,
            expires_at=now + timedelta(hours=1),
        )
    )
    audit = AuditLog(workdir / "audit.log")
    return GuardedFilesystem(store, audit), audit, agent


def main() -> None:
    workdir = Path(tempfile.mkdtemp(prefix="renker_example_"))
    (workdir / "project").mkdir(parents=True)
    (workdir / "project" / "example.txt").write_text("hello from the project", encoding="utf-8")

    guard, audit, agent = build_guard(workdir)

    allowed = guard.read(agent, str(workdir / "project" / "example.txt"))
    print("ALLOWED READ  ->", allowed.decision.value, "|", repr(allowed.value))

    denied = guard.read(agent, str(workdir / ".ssh" / "config"))
    print("DENIED READ   ->", denied.decision.value, "|", denied.reason)

    assert allowed.decision is Decision.ALLOW
    assert denied.decision is Decision.DENY

    print("\nAudit trail:")
    for event in audit.query(actor=agent.urn):
        print(f"  {event.policy_decision:6}  {event.action}  {event.outcome}")
    audit.verify()
    print("\naudit.verify() -> OK")


if __name__ == "__main__":
    main()
