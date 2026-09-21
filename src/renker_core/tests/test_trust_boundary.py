from __future__ import annotations

import dataclasses
import inspect
from datetime import datetime, timezone

import pytest

from renker_core.capabilities import Capability, CapabilityStore, PathScope
from renker_core.identity import Actor
from renker_core.policy import Decision, evaluate


def _store(tmp_path, **overrides):
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
    store.grant(Capability(**base))
    return store


def _decide(store, tmp_path, actor="agent:a", action="filesystem.write", target="drafts/x"):
    return evaluate(
        actor=Actor.from_urn(actor),
        action=action,
        target=str(tmp_path / target),
        store=store,
    ).decision


class TestPromptInjection:
    def test_injected_request_to_read_credentials_denied(self, tmp_path):
        store = _store(tmp_path)
        decision = _decide(store, tmp_path, action="filesystem.read", target=".ssh/id_rsa")
        assert decision is Decision.DENY

    def test_injected_request_outside_scope_denied(self, tmp_path):
        store = _store(tmp_path)
        assert _decide(store, tmp_path, target="../secrets/passwords.txt") is Decision.DENY

    def test_tool_output_claiming_authorization_has_no_effect(self, tmp_path):
        store = _store(tmp_path)
        decision = _decide(store, tmp_path, action="filesystem.read", target="drafts/x")
        assert decision is Decision.DENY


class TestConfusedDeputy:
    def test_other_actor_cannot_use_grant(self, tmp_path):
        store = _store(tmp_path)
        assert _decide(store, tmp_path, actor="agent:b") is Decision.DENY

    def test_same_identifier_different_kind_is_distinct(self, tmp_path):
        store = _store(tmp_path)
        assert _decide(store, tmp_path, actor="human:a") is Decision.DENY

    def test_authority_does_not_transfer_to_other_target(self, tmp_path):
        store = _store(tmp_path)
        assert _decide(store, tmp_path, target="other/y") is Decision.DENY


class TestRiskIsNotRequestControlled:
    def test_evaluate_has_no_request_authorization_input(self):
        params = set(inspect.signature(evaluate).parameters)
        forbidden = ("context", "risk", "risk_tier", "approval_policy", "authorized", "trusted")
        for name in forbidden:
            assert name not in params

    def test_capability_is_immutable(self, tmp_path):
        store = _store(tmp_path, approval_policy="human", risk_tier="critical")
        cap = store.find("agent:a", "filesystem.write")[0]
        with pytest.raises(dataclasses.FrozenInstanceError):
            cap.approval_policy = "auto"  # type: ignore[misc]
        with pytest.raises(dataclasses.FrozenInstanceError):
            cap.risk_tier = "low"  # type: ignore[misc]

    def test_human_approval_policy_forces_require_approval(self, tmp_path):
        store = _store(tmp_path, approval_policy="human")
        assert _decide(store, tmp_path) is Decision.REQUIRE_APPROVAL

    def test_risk_tier_does_not_loosen_scope(self, tmp_path):
        store = _store(tmp_path, risk_tier="low")
        assert _decide(store, tmp_path, target="outside/x") is Decision.DENY


class TestFailClosed:
    def test_unknown_action_denied(self, tmp_path):
        store = _store(tmp_path)
        assert _decide(store, tmp_path, action="filesystem.chmod") is Decision.DENY

    def test_no_grants_denied(self, tmp_path):
        assert _decide(CapabilityStore(), tmp_path) is Decision.DENY
