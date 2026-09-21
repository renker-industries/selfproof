from __future__ import annotations

import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from renker_core.audit import AuditLog
from renker_core.capabilities import Capability, CapabilityStore, PathScope
from renker_core.identity import Actor
from renker_core.integration import GuardedFilesystem


def _rule(title: str) -> None:
    print()
    print("=" * 68)
    print(title)
    print("=" * 68)


def _show(step: str, result) -> None:
    print(f"\n[{step}]")
    print(f"  decision : {result.decision.value}")
    print(f"  reason   : {result.reason}")
    print(f"  executed : {result.executed}")
    print(f"  audit    : {result.event.event_id} ({result.event.outcome})")


def main() -> None:
    workdir = Path(tempfile.mkdtemp(prefix="renker_demo_"))
    drafts = workdir / "Documents" / "drafts"
    now = datetime.now(timezone.utc)

    agent = Actor("agent", "rencora-session-8f2c")
    owner = Actor("human", "sebastian")

    store = CapabilityStore()
    store.grant(
        Capability(
            capability="filesystem.write",
            scope=PathScope(base=str(drafts)),
            granted_to=agent.urn,
            granted_by=owner.urn,
            issued_at=now,
            expires_at=now + timedelta(hours=1),
            approval_policy="auto",
            risk_tier="low",
        )
    )
    store.grant(
        Capability(
            capability="filesystem.read",
            scope=PathScope(base=str(drafts)),
            granted_to=agent.urn,
            granted_by=owner.urn,
            issued_at=now,
            expires_at=now + timedelta(hours=1),
            approval_policy="auto",
            risk_tier="low",
        )
    )

    audit = AuditLog(workdir / "audit.log")
    guard = GuardedFilesystem(store, audit)

    _rule("RENKER first platform slice: identity -> capability -> policy -> audit")
    print(f"actor : {agent.urn}")
    print(f"scope : {PathScope(base=str(drafts)).describe()}")

    _rule('1) Rencora: "write my report into drafts"  (expected ALLOW)')
    write_result = guard.write(agent, str(drafts / "report.md"), "quarterly notes")
    _show("filesystem.write drafts/report.md", write_result)

    _rule('2) Rencora: "read my report back"  (expected ALLOW)')
    read_result = guard.read(agent, str(drafts / "report.md"))
    _show("filesystem.read drafts/report.md", read_result)
    print(f"  content  : {read_result.value!r}")

    _rule('3) Manipulated agent: "read ~/.ssh/config"  (expected DENY)')
    ssh_like = workdir / ".ssh" / "config"
    ssh_result = guard.read(agent, str(ssh_like))
    _show("filesystem.read .ssh/config", ssh_result)

    _rule('4) Manipulated agent: "write outside drafts via .."  (expected DENY)')
    traversal = str(drafts / ".." / ".." / "secret.txt")
    traversal_result = guard.write(agent, traversal, "exfiltrated")
    _show("filesystem.write ../../secret.txt", traversal_result)

    _rule("Audit trail (tamper-evident)")
    for event in audit.read_all():
        print(f"  {event.timestamp}  {event.policy_decision:16}  {event.action}  {event.outcome}")
    audit.verify()
    print("\n  audit.verify() -> OK (chain and head anchor intact)")


if __name__ == "__main__":
    main()
