from __future__ import annotations

from datetime import datetime, timedelta, timezone

from renker_core import (
    Action,
    Capability,
    CapabilityStore,
    Context,
    Effect,
    Identity,
    PathScope,
    Policy,
    Resource,
    Rule,
    StaticPolicyEngine,
)


def _store(tmp_path, approval="auto", verb="write", expires=None):
    store = CapabilityStore()
    store.grant(
        Capability(
            capability=f"filesystem.{verb}",
            scope=PathScope(base=str(tmp_path / "allowed")),
            granted_to="agent:a",
            granted_by="human:o",
            issued_at=datetime.now(timezone.utc),
            expires_at=expires,
            approval_policy=approval,
        )
    )
    return store


def _engine(store, rules=()):
    return StaticPolicyEngine(store, Policy("test", "1", rules=rules))


def _who():
    return Identity("agent", "a")


def _act(verb="write"):
    return Action("filesystem", verb)


def _res(tmp_path, sub="allowed", name="x.txt"):
    return Resource("file", str(tmp_path / sub / name))


def test_allow(tmp_path):
    d = _engine(_store(tmp_path)).evaluate(
        subject=_who(), action=_act(), resource=_res(tmp_path), context=Context()
    )
    assert d.effect is Effect.ALLOW
    assert d.policy_id == "test" and d.policy_version == "1" and d.capability_id


def test_deny_out_of_scope(tmp_path):
    d = _engine(_store(tmp_path)).evaluate(
        subject=_who(), action=_act(), resource=_res(tmp_path, "outside"), context=Context()
    )
    assert d.effect is Effect.DENY


def test_deny_wrong_action(tmp_path):
    d = _engine(_store(tmp_path)).evaluate(
        subject=_who(), action=_act("read"), resource=_res(tmp_path), context=Context()
    )
    assert d.effect is Effect.DENY


def test_capability_human_requires_approval(tmp_path):
    d = _engine(_store(tmp_path, approval="human")).evaluate(
        subject=_who(), action=_act(), resource=_res(tmp_path), context=Context()
    )
    assert d.effect is Effect.REQUIRE_APPROVAL


def test_rule_deny_overrides(tmp_path):
    rule = Rule("r", Effect.DENY, "blocked by rule", action=_act())
    d = _engine(_store(tmp_path), rules=(rule,)).evaluate(
        subject=_who(), action=_act(), resource=_res(tmp_path), context=Context()
    )
    assert d.effect is Effect.DENY and d.reason == "blocked by rule"


def test_rule_env_file_requires_approval(tmp_path):
    rule = Rule("r", Effect.REQUIRE_APPROVAL, "env files need approval", resource_glob="*.env")
    d = _engine(_store(tmp_path), rules=(rule,)).evaluate(
        subject=_who(), action=_act(), resource=_res(tmp_path, name="config.env"), context=Context()
    )
    assert d.effect is Effect.REQUIRE_APPROVAL


def test_allow_rule_never_loosens(tmp_path):
    rule = Rule("r", Effect.ALLOW, "noop", action=_act())
    d = _engine(_store(tmp_path, approval="human"), rules=(rule,)).evaluate(
        subject=_who(), action=_act(), resource=_res(tmp_path), context=Context()
    )
    assert d.effect is Effect.REQUIRE_APPROVAL


def test_production_no_human_destructive_requires_approval(tmp_path):
    rule = Rule(
        "r",
        Effect.REQUIRE_APPROVAL,
        "prod destructive without human",
        environments=("production",),
        only_when_user_absent=True,
        min_risk_tier="high",
    )
    d = _engine(_store(tmp_path, verb="delete"), rules=(rule,)).evaluate(
        subject=_who(),
        action=_act("delete"),
        resource=_res(tmp_path),
        context=Context(environment="production", user_present=False),
    )
    assert d.effect is Effect.REQUIRE_APPROVAL


def test_expired_capability_denied(tmp_path):
    past = datetime.now(timezone.utc) - timedelta(minutes=1)
    d = _engine(_store(tmp_path, expires=past)).evaluate(
        subject=_who(), action=_act(), resource=_res(tmp_path), context=Context()
    )
    assert d.effect is Effect.DENY


def test_expired_identity_denied(tmp_path):
    who = Identity("agent", "a", expires_at=datetime.now(timezone.utc) - timedelta(hours=1))
    d = _engine(_store(tmp_path)).evaluate(
        subject=who, action=_act(), resource=_res(tmp_path), context=Context()
    )
    assert d.effect is Effect.DENY and "expired" in d.reason


def test_determinism_same_input_same_effect(tmp_path):
    engine = _engine(_store(tmp_path))
    d1 = engine.evaluate(subject=_who(), action=_act(), resource=_res(tmp_path), context=Context())
    d2 = engine.evaluate(subject=_who(), action=_act(), resource=_res(tmp_path), context=Context())
    stable = lambda d: (  # noqa: E731
        d.effect,
        d.reason,
        d.obligations,
        d.subject,
        d.action,
        d.resource,
        d.policy_id,
        d.policy_version,
    )
    assert stable(d1) == stable(d2)
    assert d1.decision_id != d2.decision_id
