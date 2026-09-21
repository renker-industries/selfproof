from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from renker_core.audit import AuditLog
from renker_core.capabilities import Capability, CapabilityStore, PathScope
from renker_core.identity import Actor, IdentityError
from renker_core.integration import GuardedFilesystem
from renker_core.policy import Decision, evaluate


def _store_with(tmp_path, **overrides):
    store = CapabilityStore()
    base = dict(
        capability="filesystem.write",
        scope=PathScope(base=str(tmp_path / "drafts")),
        granted_to="agent:a",
        granted_by="human:sebastian",
        issued_at=datetime.now(timezone.utc),
        expires_at=None,
    )
    base.update(overrides)
    cap = Capability(**base)
    cid = store.grant(cap)
    return store, cid


def _guard(tmp_path, store):
    return GuardedFilesystem(store, AuditLog(tmp_path / "audit.log"))


def test_attack_path_traversal(tmp_path):
    store, _ = _store_with(tmp_path)
    guard = _guard(tmp_path, store)
    target = str(tmp_path / "drafts" / ".." / "secret.txt")
    result = guard.write(Actor("agent", "a"), target, "x")
    assert result.decision is Decision.DENY
    assert result.executed is False


def test_attack_prefix_confusion(tmp_path):
    store, _ = _store_with(tmp_path, scope=PathScope(base=str(tmp_path / "Documents")))
    result = evaluate(
        actor=Actor("agent", "a"),
        action="filesystem.write",
        target=str(tmp_path / "Documents2" / "x.txt"),
        store=store,
    )
    assert result.decision is Decision.DENY


def test_attack_expired_capability(tmp_path):
    past = datetime.now(timezone.utc) - timedelta(minutes=1)
    store, _ = _store_with(tmp_path, issued_at=past - timedelta(hours=1), expires_at=past)
    result = evaluate(
        actor=Actor("agent", "a"),
        action="filesystem.write",
        target=str(tmp_path / "drafts" / "x.txt"),
        store=store,
    )
    assert result.decision is Decision.DENY
    assert "expired" in result.reason


def test_attack_wrong_actor(tmp_path):
    store, _ = _store_with(tmp_path)
    result = evaluate(
        actor=Actor("agent", "b"),
        action="filesystem.write",
        target=str(tmp_path / "drafts" / "x.txt"),
        store=store,
    )
    assert result.decision is Decision.DENY


def test_attack_wrong_operation(tmp_path):
    store, _ = _store_with(tmp_path)
    result = evaluate(
        actor=Actor("agent", "a"),
        action="filesystem.read",
        target=str(tmp_path / "drafts" / "x.txt"),
        store=store,
    )
    assert result.decision is Decision.DENY


def test_attack_wrong_target(tmp_path):
    store, _ = _store_with(tmp_path)
    result = evaluate(
        actor=Actor("agent", "a"),
        action="filesystem.write",
        target=str(tmp_path / "elsewhere" / "x.txt"),
        store=store,
    )
    assert result.decision is Decision.DENY


def test_attack_revocation_mid_lifetime(tmp_path):
    store, cid = _store_with(tmp_path)
    store.revoke(cid)
    result = evaluate(
        actor=Actor("agent", "a"),
        action="filesystem.write",
        target=str(tmp_path / "drafts" / "x.txt"),
        store=store,
    )
    assert result.decision is Decision.DENY
    assert "revoked" in result.reason


def test_attack_malformed_actor_is_rejected():
    with pytest.raises(IdentityError):
        Actor("agent", "../../etc/passwd")


def test_every_decision_produces_audit_event(tmp_path):
    store, _ = _store_with(tmp_path)
    guard = _guard(tmp_path, store)
    allow = guard.write(Actor("agent", "a"), str(tmp_path / "drafts" / "ok.txt"), "x")
    deny = guard.write(Actor("agent", "a"), str(tmp_path / "no.txt"), "x")
    events = guard._audit.read_all()
    assert allow.event.entry_hash in {e.entry_hash for e in events}
    assert deny.event.entry_hash in {e.entry_hash for e in events}
    assert len(events) == 2
    guard._audit.verify()
