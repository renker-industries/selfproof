from __future__ import annotations

import dataclasses
from datetime import datetime, timedelta, timezone

import pytest

from renker_core import (
    Action,
    Context,
    Decision,
    Effect,
    Identity,
    IdentityError,
    ModelError,
    Permission,
    Resource,
    ResourcePattern,
)
from renker_core.risk import assess


def test_action_dotted_and_parse():
    a = Action("filesystem", "write")
    assert a.dotted == "filesystem.write"
    assert Action.parse("filesystem.write") == a


def test_action_rejects_dot_in_parts():
    with pytest.raises(ModelError):
        Action("file.system", "write")


def test_action_parse_rejects_bad():
    with pytest.raises(ModelError):
        Action.parse("filesystem")


def test_resource_urn():
    assert Resource("file", "/x").urn == "file:/x"


def test_resource_rejects_empty_identifier():
    with pytest.raises(ModelError):
        Resource("file", "")


def test_pattern_matches_inside(tmp_path):
    p = ResourcePattern(base=str(tmp_path / "a"))
    assert p.matches(Resource("file", str(tmp_path / "a" / "x")))


def test_pattern_rejects_traversal(tmp_path):
    p = ResourcePattern(base=str(tmp_path / "a"))
    assert not p.matches(Resource("file", str(tmp_path / "a" / ".." / "secret")))


def test_pattern_rejects_prefix_confusion(tmp_path):
    p = ResourcePattern(base=str(tmp_path / "Docs"))
    assert not p.matches(Resource("file", str(tmp_path / "Docs2" / "x")))


def test_pattern_rejects_empty_base():
    with pytest.raises(ModelError):
        ResourcePattern(base="")


def test_context_default_and_env_validation():
    assert Context().environment == "unknown"
    with pytest.raises(ModelError):
        Context(environment="prod")


def test_identity_urn_and_expiry():
    assert Identity("agent", "s1").urn == "agent:s1"
    past = datetime.now(timezone.utc) - timedelta(hours=1)
    assert Identity("agent", "s1", expires_at=past).is_expired()
    assert not Identity("agent", "s1").is_expired()


def test_identity_naive_expiry_rejected():
    with pytest.raises(IdentityError):
        Identity("agent", "s1", expires_at=datetime.now())  # noqa: DTZ005


def test_identity_bad_kind_rejected():
    with pytest.raises(IdentityError):
        Identity("robot", "s1")


def test_permission_permits(tmp_path):
    perm = Permission(Action("filesystem", "write"), ResourcePattern(base=str(tmp_path / "a")))
    assert perm.permits(Action("filesystem", "write"), Resource("file", str(tmp_path / "a" / "x")))
    assert not perm.permits(
        Action("filesystem", "read"), Resource("file", str(tmp_path / "a" / "x"))
    )


def test_decision_roundtrip_and_flags():
    d = Decision(
        effect=Effect.ALLOW,
        subject="agent:a",
        action="filesystem.write",
        resource="file:/x",
        policy_id="p",
        policy_version="1",
        reason="ok",
    )
    assert d.is_allowed
    assert Decision.from_dict(d.to_dict()) == d


def test_decision_is_immutable():
    d = Decision(
        effect=Effect.DENY,
        subject="a",
        action="x",
        resource="r",
        policy_id="p",
        policy_version="1",
        reason="n",
    )
    with pytest.raises(dataclasses.FrozenInstanceError):
        d.effect = Effect.ALLOW  # type: ignore[misc]


def test_risk_flags_destructive_sensitive():
    r = assess(
        Action("filesystem", "delete"),
        Resource("file", "/home/u/.ssh/id_rsa"),
        Context(environment="production", user_present=False),
    )
    assert r.tier in ("high", "critical")
    assert "destructive:delete" in r.factors
    assert "sensitive-resource" in r.factors
