from __future__ import annotations

from datetime import datetime, timedelta, timezone

from renker_core.audit import AuditLog
from renker_core.capabilities import Capability, CapabilityStore, PathScope
from renker_core.identity import Actor
from renker_core.integration import GuardedFilesystem
from renker_core.policy import Decision


def _grant(store, capability, scope, actor_urn, expires_at):
    store.grant(
        Capability(
            capability=capability,
            scope=PathScope(base=str(scope)),
            granted_to=actor_urn,
            granted_by="human:records-officer",
            issued_at=datetime.now(timezone.utc),
            expires_at=expires_at,
            approval_policy="auto",
            risk_tier="high",
        )
    )


def test_hospital_per_patient_isolation(tmp_path):
    records = tmp_path / "records"
    patient_a = records / "patient-123" / "notes"
    patient_b = records / "patient-456" / "notes"
    credentials = tmp_path / ".ssh" / "id_rsa"

    now = datetime.now(timezone.utc)
    store = CapabilityStore()
    agent_a = Actor("agent", "assistant-dr-alvarez")
    agent_b = Actor("agent", "assistant-dr-becker")
    _grant(store, "filesystem.write", patient_a, agent_a.urn, now + timedelta(hours=8))
    _grant(store, "filesystem.write", patient_b, agent_b.urn, now + timedelta(hours=8))

    audit = AuditLog(tmp_path / "audit.log")
    guard = GuardedFilesystem(store, audit)

    own = guard.write(agent_a, str(patient_a / "visit.md"), "vitals stable")
    assert own.decision is Decision.ALLOW
    assert (patient_a / "visit.md").read_text(encoding="utf-8") == "vitals stable"

    cross = guard.write(agent_a, str(patient_b / "visit.md"), "should not happen")
    assert cross.decision is Decision.DENY
    assert not (patient_b / "visit.md").exists()

    creds = guard.read(agent_a, str(credentials))
    assert creds.decision is Decision.DENY

    traversal = guard.write(
        agent_a, str(patient_a / ".." / ".." / "patient-456" / "leak.md"), "exfil"
    )
    assert traversal.decision is Decision.DENY

    events = audit.read_all()
    assert [e.policy_decision for e in events] == ["ALLOW", "DENY", "DENY", "DENY"]
    audit.verify()


def test_law_firm_capability_expiry_and_revocation(tmp_path):
    matter = tmp_path / "matters" / "acme-v-globex"
    now = datetime.now(timezone.utc)
    store = CapabilityStore()
    paralegal = Actor("agent", "paralegal-session-77")
    _grant(store, "filesystem.write", matter, paralegal.urn, now + timedelta(minutes=30))
    audit = AuditLog(tmp_path / "audit.log")
    guard = GuardedFilesystem(store, audit)

    ok = guard.write(paralegal, str(matter / "draft-brief.md"), "argument 1")
    assert ok.decision is Decision.ALLOW

    cid = store.find(paralegal.urn, "filesystem.write")[0].capability_id
    assert store.revoke(cid) is True

    after = guard.write(paralegal, str(matter / "draft-brief-2.md"), "argument 2")
    assert after.decision is Decision.DENY
    assert not (matter / "draft-brief-2.md").exists()
    audit.verify()
