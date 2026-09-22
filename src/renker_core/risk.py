from __future__ import annotations

from dataclasses import dataclass

from renker_core.model import Action, Context, Resource

RISK_TIERS = ("low", "medium", "high", "critical")

_DESTRUCTIVE_VERBS = frozenset({"delete", "remove", "destroy", "drop", "wipe", "overwrite"})
_SENSITIVE_MARKERS = (".ssh", ".env", "secret", "credential", "password", "id_rsa")


@dataclass(frozen=True)
class RiskAssessment:
    score: int
    factors: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not 0 <= self.score <= 100:
            raise ValueError(f"risk score out of range: {self.score}")

    @property
    def tier(self) -> str:
        if self.score >= 80:
            return "critical"
        if self.score >= 50:
            return "high"
        if self.score >= 20:
            return "medium"
        return "low"


def assess(action: Action, resource: Resource, context: Context) -> RiskAssessment:
    score = 0
    factors: list[str] = []
    if action.verb in _DESTRUCTIVE_VERBS:
        score += 40
        factors.append(f"destructive:{action.verb}")
    lowered = resource.identifier.lower()
    if any(marker in lowered for marker in _SENSITIVE_MARKERS):
        score += 40
        factors.append("sensitive-resource")
    if context.environment == "production":
        score += 15
        factors.append("production")
    if not context.user_present:
        score += 10
        factors.append("no-human-present")
    return RiskAssessment(score=min(score, 100), factors=tuple(factors))


__all__ = ["RISK_TIERS", "RiskAssessment", "assess"]
