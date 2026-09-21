from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from renker_core.decision import Decision
from renker_core.effect import Effect


class ApprovalError(Exception):
    pass


def _now(now: datetime | None) -> datetime:
    return now if now is not None else datetime.now(timezone.utc)


@dataclass(frozen=True)
class ApprovalRequest:
    request_id: str
    decision_id: str
    subject: str
    action: str
    resource: str
    created_at: datetime
    expires_at: datetime

    def is_expired(self, now: datetime | None = None) -> bool:
        return _now(now) >= self.expires_at


@dataclass(frozen=True)
class Approval:
    approval_id: str
    request_id: str
    decision_id: str
    approver: str
    granted_at: datetime


class ApprovalStore:
    def __init__(self, ttl_seconds: int = 3600) -> None:
        self._ttl = ttl_seconds
        self._requests: dict[str, ApprovalRequest] = {}
        self._by_decision: dict[str, str] = {}
        self._approvals: dict[str, Approval] = {}
        self._consumed: set[str] = set()

    def create_request(self, decision: Decision, now: datetime | None = None) -> ApprovalRequest:
        if decision.effect is not Effect.REQUIRE_APPROVAL:
            raise ApprovalError("only REQUIRE_APPROVAL decisions can create an approval request")
        moment = _now(now)
        request = ApprovalRequest(
            request_id="apr_" + uuid.uuid4().hex,
            decision_id=decision.decision_id,
            subject=decision.subject,
            action=decision.action,
            resource=decision.resource,
            created_at=moment,
            expires_at=moment + timedelta(seconds=self._ttl),
        )
        self._requests[request.request_id] = request
        self._by_decision[decision.decision_id] = request.request_id
        return request

    def approve(self, request_id: str, approver: str, now: datetime | None = None) -> Approval:
        request = self._requests.get(request_id)
        if request is None:
            raise ApprovalError(f"unknown approval request: {request_id}")
        if request.is_expired(now):
            raise ApprovalError("approval request has expired")
        if request_id in self._approvals:
            raise ApprovalError("approval request already approved")
        approval = Approval(
            approval_id="apv_" + uuid.uuid4().hex,
            request_id=request_id,
            decision_id=request.decision_id,
            approver=approver,
            granted_at=_now(now),
        )
        self._approvals[request_id] = approval
        return approval

    def is_satisfied(
        self,
        decision_id: str,
        subject: str,
        action: str,
        resource: str,
        now: datetime | None = None,
    ) -> bool:
        request_id = self._by_decision.get(decision_id)
        if request_id is None or request_id in self._consumed:
            return False
        request = self._requests[request_id]
        if request.is_expired(now):
            return False
        if request.subject != subject or request.action != action or request.resource != resource:
            return False
        return request_id in self._approvals

    def consume(self, decision_id: str) -> bool:
        request_id = self._by_decision.get(decision_id)
        if request_id is None or request_id not in self._approvals or request_id in self._consumed:
            return False
        self._consumed.add(request_id)
        return True


__all__ = ["ApprovalError", "ApprovalRequest", "Approval", "ApprovalStore"]
