from __future__ import annotations

import uuid
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone

from renker_core.approval import ApprovalStore
from renker_core.audit.log import AuditSink
from renker_core.decision import Decision
from renker_core.effect import Effect
from renker_core.identity.subject import Identity
from renker_core.model import Action, Context, Resource
from renker_core.policy.engine import PolicyEngine
from renker_core.replay import ReplayGuard

_AUTHORIZER_POLICY_ID = "renker-core/authorizer"
_AUTHORIZER_POLICY_VERSION = "1"


def _now(now: datetime | None) -> datetime:
    return now if now is not None else datetime.now(timezone.utc)


@dataclass(frozen=True)
class AuthorizationRequest:
    subject: Identity
    action: Action
    resource: Resource
    context: Context
    request_id: str = field(default_factory=lambda: "req_" + uuid.uuid4().hex)
    nonce: str = field(default_factory=lambda: uuid.uuid4().hex)
    issued_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime | None = None
    approved_decision_id: str | None = None


class Authorizer:
    def __init__(
        self,
        engine: PolicyEngine,
        audit: AuditSink,
        replay_guard: ReplayGuard | None = None,
        approvals: ApprovalStore | None = None,
    ) -> None:
        self._engine = engine
        self._audit = audit
        self._replay_guard = replay_guard
        self._approvals = approvals

    def authorize(self, request: AuthorizationRequest, now: datetime | None = None) -> Decision:
        try:
            decision = self._decide(request, now)
        except Exception as error:
            decision = self._deny(request, f"internal error, failing closed: {error}")
        self._audit.record_decision(decision, outcome=_outcome(decision.effect))
        return decision

    def _decide(self, request: AuthorizationRequest, now: datetime | None) -> Decision:
        moment = _now(now)
        if request.subject.is_expired(moment):
            return self._deny(request, "identity has expired")
        if request.expires_at is not None and moment >= request.expires_at:
            return self._deny(request, "authorization request has expired")
        if self._replay_guard is not None and not self._replay_guard.check(
            nonce=request.nonce, issued_at=request.issued_at, now=moment
        ):
            return self._deny(request, "request nonce is stale or already used (replay)")

        decision = self._engine.evaluate(
            subject=request.subject,
            action=request.action,
            resource=request.resource,
            context=request.context,
        )

        if decision.needs_approval and self._approvals is not None and request.approved_decision_id:
            if self._approvals.is_satisfied(
                request.approved_decision_id,
                subject=decision.subject,
                action=decision.action,
                resource=decision.resource,
                now=moment,
            ) and self._approvals.consume(request.approved_decision_id):
                return replace(
                    decision,
                    effect=Effect.ALLOW,
                    reason=f"approved via {request.approved_decision_id}",
                    obligations=decision.obligations
                    + (f"approved:{request.approved_decision_id}",),
                )
        return decision

    def _deny(self, request: AuthorizationRequest, reason: str) -> Decision:
        return Decision(
            effect=Effect.DENY,
            subject=request.subject.urn,
            action=request.action.dotted,
            resource=request.resource.urn,
            policy_id=_AUTHORIZER_POLICY_ID,
            policy_version=_AUTHORIZER_POLICY_VERSION,
            reason=reason,
        )


def _outcome(effect: Effect) -> str:
    if effect is Effect.ALLOW:
        return "allowed"
    if effect is Effect.REQUIRE_APPROVAL:
        return "pending-approval"
    return "denied"


__all__ = ["AuthorizationRequest", "Authorizer"]
