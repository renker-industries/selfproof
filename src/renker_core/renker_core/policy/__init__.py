from __future__ import annotations

from renker_core.effect import Effect
from renker_core.policy.engine import (
    Decision,
    PolicyEngine,
    PolicyResult,
    StaticPolicyEngine,
    evaluate,
)
from renker_core.policy.policy import Policy, Rule

PRIMITIVE = "policy"

RISK_TIERS = ("low", "medium", "high", "critical")

DECISIONS = ("ALLOW", "DENY", "REQUIRE_APPROVAL")

__all__ = [
    "PRIMITIVE",
    "RISK_TIERS",
    "DECISIONS",
    "Effect",
    "Decision",
    "PolicyResult",
    "evaluate",
    "PolicyEngine",
    "StaticPolicyEngine",
    "Policy",
    "Rule",
]
