from __future__ import annotations

from datetime import datetime, timedelta, timezone

from renker_core import (
    Action,
    ApprovalStore,
    AuthorizationRequest,
    Authorizer,
    Capability,
    CapabilityStore,
    Context,
    Effect,
    Identity,
    InMemoryAuditSink,
    PathScope,
    Policy,
    ReplayGuard,
    Resource,
    StaticPolicyEngine,
)


def _setup(tmp_path, approval="auto", rules=()):
    store = CapabilityStore()
    store.grant(
        Capability(
            capability="filesystem.write",
            scope=PathScope(base=str(tmp_path / "allowed")),
            granted_to="agent:a",
            granted_by="human:o",
            issued_at=datetime.now(timezone.utc),
            expires_at=None,
            approval_policy=approval,
        )
    )
    return StaticPolicyEngine(store, Policy("p", "1", rules=rules)), InMemoryAuditSink()


def _req(tmp_path, sub="allowed", name="x", **kw):
    return AuthorizationRequest(
        subject=Identity("agent", "a"),
        action=Action("filesystem", "write"),
        resource=Resource("file", str(tmp_path / sub / name)),
        context=Context(),
        **kw,
    )


def test_full_allow_is_audited(tmp_path):
    engine, sink = _setup(tmp_path)
    auth = Authorizer(engine, sink)
    d = auth.authorize(_req(tmp_path))
    assert d.is_allowed
    events = sink.events()
    assert len(events) == 1 and events[0].decision_id == d.decision_id
    sink.verify()


def test_full_deny_out_of_scope_is_audited(tmp_path):
    engine, sink = _setup(tmp_path)
    d = Authorizer(engine, sink).authorize(_req(tmp_path, sub="outside"))
    assert d.effect is Effect.DENY
    assert sink.events()[0].policy_decision == "DENY"


def test_replay_same_nonce_denied(tmp_path):
    engine, sink = _setup(tmp_path)
    auth = Authorizer(engine, sink, replay_guard=ReplayGuard())
    req = _req(tmp_path)
    assert auth.authorize(req).is_allowed
    replayed = auth.authorize(req)
    assert replayed.effect is Effect.DENY and "replay" in replayed.reason


def test_stale_request_denied(tmp_path):
    engine, sink = _setup(tmp_path)
    auth = Authorizer(engine, sink, replay_guard=ReplayGuard(ttl_seconds=1))
    old = datetime.now(timezone.utc) - timedelta(minutes=5)
    d = auth.authorize(_req(tmp_path, issued_at=old))
    assert d.effect is Effect.DENY


def test_expired_request_denied(tmp_path):
    engine, sink = _setup(tmp_path)
    past = datetime.now(timezone.utc) - timedelta(seconds=1)
    d = Authorizer(engine, sink).authorize(_req(tmp_path, expires_at=past))
    assert d.effect is Effect.DENY and "expired" in d.reason


def test_approval_flow_and_replay_protection(tmp_path):
    engine, sink = _setup(tmp_path, approval="human")
    approvals = ApprovalStore()
    auth = Authorizer(engine, sink, approvals=approvals)

    pending = auth.authorize(_req(tmp_path))
    assert pending.effect is Effect.REQUIRE_APPROVAL

    request = approvals.create_request(pending)
    approvals.approve(request.request_id, "human:boss")

    granted = auth.authorize(_req(tmp_path, approved_decision_id=pending.decision_id))
    assert granted.is_allowed

    reused = auth.authorize(_req(tmp_path, approved_decision_id=pending.decision_id))
    assert reused.effect is Effect.REQUIRE_APPROVAL


def test_approval_cannot_be_reused_for_other_action(tmp_path):
    engine, sink = _setup(tmp_path, approval="human")
    approvals = ApprovalStore()
    auth = Authorizer(engine, sink, approvals=approvals)
    pending = auth.authorize(_req(tmp_path, name="a"))
    request = approvals.create_request(pending)
    approvals.approve(request.request_id, "human:boss")
    other = auth.authorize(_req(tmp_path, name="b", approved_decision_id=pending.decision_id))
    assert other.effect is Effect.REQUIRE_APPROVAL


def test_expired_identity_denied(tmp_path):
    engine, sink = _setup(tmp_path)
    who = Identity("agent", "a", expires_at=datetime.now(timezone.utc) - timedelta(hours=1))
    req = AuthorizationRequest(
        subject=who,
        action=Action("filesystem", "write"),
        resource=Resource("file", str(tmp_path / "allowed" / "x")),
        context=Context(),
    )
    d = Authorizer(engine, sink).authorize(req)
    assert d.effect is Effect.DENY and "expired" in d.reason


def test_fail_closed_on_engine_error(tmp_path):
    class Boom:
        def evaluate(self, **kwargs):
            raise RuntimeError("boom")

    d = Authorizer(Boom(), InMemoryAuditSink()).authorize(_req(tmp_path))
    assert d.effect is Effect.DENY and "failing closed" in d.reason
