from __future__ import annotations

from dataclasses import dataclass
from fnmatch import fnmatch

from renker_core.effect import Effect
from renker_core.model import Action, Context, Resource
from renker_core.risk import RISK_TIERS, RiskAssessment


def _tier_rank(tier: str) -> int:
    return RISK_TIERS.index(tier) if tier in RISK_TIERS else -1


@dataclass(frozen=True)
class Rule:
    rule_id: str
    effect: Effect
    reason: str
    action: Action | None = None
    resource_glob: str | None = None
    environments: tuple[str, ...] = ()
    only_when_user_absent: bool = False
    min_risk_tier: str | None = None
    obligations: tuple[str, ...] = ()

    def matches(
        self,
        action: Action,
        resource: Resource,
        context: Context,
        risk: RiskAssessment,
    ) -> bool:
        if self.effect is Effect.ALLOW:
            return False
        if self.action is not None and self.action != action:
            return False
        if self.resource_glob is not None and not fnmatch(resource.identifier, self.resource_glob):
            return False
        if self.environments and context.environment not in self.environments:
            return False
        if self.only_when_user_absent and context.user_present:
            return False
        if self.min_risk_tier is not None and _tier_rank(risk.tier) < _tier_rank(
            self.min_risk_tier
        ):
            return False
        return True


@dataclass(frozen=True)
class Policy:
    policy_id: str
    version: str
    rules: tuple[Rule, ...] = ()


__all__ = ["Rule", "Policy"]
