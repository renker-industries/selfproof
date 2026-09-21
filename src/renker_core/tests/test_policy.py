from __future__ import annotations

from datetime import datetime, timezone

from renker_core.capabilities import Capability, CapabilityStore, PathScope
from renker_core.identity import Actor
from renker_core.policy import Decision, evaluate


def _grant(store, tmp_path, **overrides):
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
    store.grant(cap)
    return cap


def test_allow(tmp_path):
    store = CapabilityStore()
    _grant(store, tmp_path)
    result = evaluate(
        actor=Actor("agent", "a"),
        action="filesystem.write",
        target=str(tmp_path / "drafts" / "x.txt"),
        store=store,
    )
    assert result.decision is Decision.ALLOW


def test_deny_no_capability(tmp_path):
    store = CapabilityStore()
    result = evaluate(
        actor=Actor("agent", "a"),
        action="filesystem.write",
        target=str(tmp_path / "drafts" / "x.txt"),
        store=store,
    )
    assert result.decision is Decision.DENY
    assert "no capability" in result.reason


def test_require_approval(tmp_path):
    store = CapabilityStore()
    _grant(store, tmp_path, approval_policy="human")
    result = evaluate(
        actor=Actor("agent", "a"),
        action="filesystem.write",
        target=str(tmp_path / "drafts" / "x.txt"),
        store=store,
    )
    assert result.decision is Decision.REQUIRE_APPROVAL


def test_deny_out_of_scope_is_explainable(tmp_path):
    store = CapabilityStore()
    _grant(store, tmp_path)
    result = evaluate(
        actor=Actor("agent", "a"),
        action="filesystem.write",
        target=str(tmp_path / "secret.txt"),
        store=store,
    )
    assert result.decision is Decision.DENY
    assert result.allowed_scope is not None
    assert "outside capability scope" in result.reason
