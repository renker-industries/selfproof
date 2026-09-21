from __future__ import annotations

from datetime import datetime, timezone

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

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
    ResourcePattern,
    StaticPolicyEngine,
)

_component = st.one_of(
    st.sampled_from(["a", "b", "allowed", "allowed2", "..", "sub", "x"]),
    st.text(alphabet="abc012", min_size=1, max_size=4),
)


def _engine(tmp_path):
    store = CapabilityStore()
    store.grant(
        Capability(
            capability="filesystem.write",
            scope=PathScope(base=str(tmp_path / "allowed")),
            granted_to="agent:a",
            granted_by="human:o",
            issued_at=datetime.now(timezone.utc),
            expires_at=None,
        )
    )
    return StaticPolicyEngine(store, Policy("p", "1"))


@settings(max_examples=300, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(components=st.lists(_component, min_size=0, max_size=6))
def test_allow_implies_resource_in_scope(tmp_path, components):
    engine = _engine(tmp_path)
    target = tmp_path / "allowed"
    for part in components:
        target = target / part
    decision = engine.evaluate(
        subject=Identity("agent", "a"),
        action=Action("filesystem", "write"),
        resource=Resource("file", str(target)),
        context=Context(),
    )
    if decision.effect is Effect.ALLOW:
        pattern = ResourcePattern(base=str(tmp_path / "allowed"))
        assert pattern.matches(Resource("file", str(target)))


@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    kind=st.sampled_from(["agent", "human", "device", "service"]),
    name=st.text(min_size=0, max_size=6),
)
def test_security_failure_never_allows_outside_scope(tmp_path, kind, name):
    engine = _engine(tmp_path)
    try:
        subject = Identity(kind, name)
    except Exception:
        return
    decision = engine.evaluate(
        subject=subject,
        action=Action("filesystem", "write"),
        resource=Resource("file", str(tmp_path / "outside" / "secret")),
        context=Context(),
    )
    assert decision.effect is not Effect.ALLOW
