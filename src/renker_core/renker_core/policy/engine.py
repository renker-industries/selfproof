from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from renker_core.capabilities.model import Capability
from renker_core.capabilities.store import CapabilityStore
from renker_core.decision import Decision as DecisionRecord
from renker_core.effect import Effect
from renker_core.identity.actor import Actor
from renker_core.identity.subject import Identity
from renker_core.model import Action, Context, Resource
from renker_core.policy.policy import Policy
from renker_core.risk import assess

Decision = Effect

_RESTRICTION_ORDER = {Effect.ALLOW: 0, Effect.REQUIRE_APPROVAL: 1, Effect.DENY: 2}


def _more_restrictive(current: Effect, candidate: Effect) -> Effect:
    return candidate if _RESTRICTION_ORDER[candidate] > _RESTRICTION_ORDER[current] else current


@dataclass(frozen=True)
class PolicyResult:
    decision: Decision
    reason: str
    actor: str
    action: str
    target: str
    allowed_scope: str | None = None
    capability_id: str | None = None


def evaluate(
    *,
    actor: Actor,
    action: str,
    target: str,
    store: CapabilityStore,
    now: datetime | None = None,
) -> PolicyResult:
    candidates = store.find(actor.urn, action)
    if not candidates:
        return PolicyResult(
            decision=Decision.DENY,
            reason=f"no capability grants {action} to {actor.urn}",
            actor=actor.urn,
            action=action,
            target=target,
        )

    last_reason = "no candidate capability matched the requested target"
    last_scope: str | None = None
    last_id: str | None = None

    for cap in candidates:
        result = _evaluate_one(
            actor=actor, action=action, target=target, cap=cap, store=store, now=now
        )
        if result.decision is not Decision.DENY:
            return result
        last_reason = result.reason
        last_scope = result.allowed_scope
        last_id = result.capability_id

    return PolicyResult(
        decision=Decision.DENY,
        reason=last_reason,
        actor=actor.urn,
        action=action,
        target=target,
        allowed_scope=last_scope,
        capability_id=last_id,
    )


def _evaluate_one(
    *,
    actor: Actor,
    action: str,
    target: str,
    cap: Capability,
    store: CapabilityStore,
    now: datetime | None,
) -> PolicyResult:
    scope = cap.scope.describe()
    base = PolicyResult(
        decision=Decision.DENY,
        reason="",
        actor=actor.urn,
        action=action,
        target=target,
        allowed_scope=scope,
        capability_id=cap.capability_id,
    )

    if cap.granted_to != actor.urn:
        return _deny(
            base,
            f"capability {cap.capability_id} is granted to {cap.granted_to}, not {actor.urn}",
        )
    if not cap.permits_action(action):
        return _deny(base, f"capability permits {cap.capability}, not {action}")
    if cap.is_expired(now):
        return _deny(base, f"capability {cap.capability_id} expired at {cap.expires_at}")
    if store.is_revoked(cap.capability_id):
        return _deny(base, f"capability {cap.capability_id} has been revoked")
    if not cap.permits_target(target):
        return _deny(base, f"target is outside capability scope {scope}")

    if cap.approval_policy == "deny":
        return _deny(base, "approval policy is deny")
    if cap.approval_policy == "human":
        return _replace(
            base, Decision.REQUIRE_APPROVAL, "approval policy requires human confirmation"
        )
    return _replace(base, Decision.ALLOW, "within capability scope, action and lifetime")


def _deny(base: PolicyResult, reason: str) -> PolicyResult:
    return _replace(base, Decision.DENY, reason)


def _replace(base: PolicyResult, decision: Decision, reason: str) -> PolicyResult:
    return PolicyResult(
        decision=decision,
        reason=reason,
        actor=base.actor,
        action=base.action,
        target=base.target,
        allowed_scope=base.allowed_scope,
        capability_id=base.capability_id,
    )


class PolicyEngine(Protocol):
    def evaluate(
        self,
        *,
        subject: Identity,
        action: Action,
        resource: Resource,
        context: Context,
    ) -> DecisionRecord: ...


_APPROVAL_EFFECT = {
    "auto": Effect.ALLOW,
    "human": Effect.REQUIRE_APPROVAL,
    "deny": Effect.DENY,
}


class StaticPolicyEngine:
    def __init__(self, store: CapabilityStore, policy: Policy) -> None:
        self._store = store
        self._policy = policy

    def evaluate(
        self,
        *,
        subject: Identity,
        action: Action,
        resource: Resource,
        context: Context,
    ) -> DecisionRecord:
        risk = assess(action, resource, context)
        obligations = [f"risk:{risk.tier}"]

        if subject.is_expired():
            return self._decision(
                Effect.DENY, subject, action, resource, "identity has expired", obligations, None
            )

        capability = self._find_capability(subject, action, resource)
        if capability is None:
            return self._decision(
                Effect.DENY,
                subject,
                action,
                resource,
                f"no capability grants {action.dotted} on {resource.identifier} to {subject.urn}",
                obligations,
                None,
            )

        effect = _APPROVAL_EFFECT.get(capability.approval_policy, Effect.DENY)
        reason = "within capability scope, action and lifetime"
        for rule in self._policy.rules:
            if rule.matches(action, resource, context, risk):
                effect = _more_restrictive(effect, rule.effect)
                obligations.extend(rule.obligations)
                reason = rule.reason
        return self._decision(
            effect, subject, action, resource, reason, obligations, capability.capability_id
        )

    def _find_capability(
        self, subject: Identity, action: Action, resource: Resource
    ) -> Capability | None:
        for candidate in self._store.find(subject.urn, action.dotted):
            if candidate.is_expired():
                continue
            if self._store.is_revoked(candidate.capability_id):
                continue
            if not candidate.permits_target(resource.identifier):
                continue
            return candidate
        return None

    def _decision(
        self,
        effect: Effect,
        subject: Identity,
        action: Action,
        resource: Resource,
        reason: str,
        obligations: list[str],
        capability_id: str | None,
    ) -> DecisionRecord:
        return DecisionRecord(
            effect=effect,
            subject=subject.urn,
            action=action.dotted,
            resource=resource.urn,
            policy_id=self._policy.policy_id,
            policy_version=self._policy.version,
            reason=reason,
            obligations=tuple(obligations),
            capability_id=capability_id,
        )
