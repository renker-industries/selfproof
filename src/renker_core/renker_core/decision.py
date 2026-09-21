from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

from renker_core.effect import Effect


def _new_id() -> str:
    return "dec_" + uuid.uuid4().hex


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class Decision:
    effect: Effect
    subject: str
    action: str
    resource: str
    policy_id: str
    policy_version: str
    reason: str
    decision_id: str = field(default_factory=_new_id)
    obligations: tuple[str, ...] = ()
    capability_id: str | None = None
    timestamp: str = field(default_factory=_now_iso)

    @property
    def is_allowed(self) -> bool:
        return self.effect is Effect.ALLOW

    @property
    def needs_approval(self) -> bool:
        return self.effect is Effect.REQUIRE_APPROVAL

    def to_dict(self) -> dict:
        return {
            "decision_id": self.decision_id,
            "effect": self.effect.value,
            "subject": self.subject,
            "action": self.action,
            "resource": self.resource,
            "policy_id": self.policy_id,
            "policy_version": self.policy_version,
            "reason": self.reason,
            "obligations": list(self.obligations),
            "capability_id": self.capability_id,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Decision:
        return cls(
            effect=Effect(data["effect"]),
            subject=data["subject"],
            action=data["action"],
            resource=data["resource"],
            policy_id=data["policy_id"],
            policy_version=data["policy_version"],
            reason=data["reason"],
            decision_id=data["decision_id"],
            obligations=tuple(data.get("obligations", ())),
            capability_id=data.get("capability_id"),
            timestamp=data["timestamp"],
        )


__all__ = ["Decision"]
