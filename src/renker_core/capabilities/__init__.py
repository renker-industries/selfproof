from __future__ import annotations

from renker_core.capabilities.model import (
    APPROVAL_POLICIES,
    RISK_TIERS,
    Capability,
    CapabilityError,
    PathScope,
)
from renker_core.capabilities.store import CapabilityStore

PRIMITIVE = "capabilities"

CAPABILITY_FIELDS = (
    "permission",
    "scope",
    "lifetime",
    "audit_trail",
    "approval_policy",
    "revocation",
)

__all__ = [
    "PRIMITIVE",
    "CAPABILITY_FIELDS",
    "APPROVAL_POLICIES",
    "RISK_TIERS",
    "Capability",
    "CapabilityError",
    "PathScope",
    "CapabilityStore",
]
