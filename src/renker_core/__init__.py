from __future__ import annotations

from renker_core.approval import Approval, ApprovalError, ApprovalRequest, ApprovalStore
from renker_core.audit import AuditError, AuditEvent, AuditLog, AuditSink, InMemoryAuditSink
from renker_core.authorize import AuthorizationRequest, Authorizer
from renker_core.capabilities import (
    Capability,
    CapabilityError,
    CapabilityStore,
    PathScope,
)
from renker_core.decision import Decision
from renker_core.effect import Effect
from renker_core.identity import Actor, Identity, IdentityError
from renker_core.integration import GuardedFilesystem, GuardResult
from renker_core.model import Action, Context, ModelError, Resource, ResourcePattern
from renker_core.permissions import Permission
from renker_core.policy import (
    Policy,
    PolicyEngine,
    PolicyResult,
    Rule,
    StaticPolicyEngine,
    evaluate,
)
from renker_core.replay import ReplayGuard
from renker_core.risk import RiskAssessment

__version__ = "0.2.0"

PRIMITIVES = (
    "identity",
    "capabilities",
    "permissions",
    "events",
    "memory",
    "tasks",
    "audit",
    "policy",
    "crypto_interface",
    "protocol",
)

__all__ = [
    "__version__",
    "PRIMITIVES",
    "Identity",
    "Actor",
    "IdentityError",
    "Action",
    "Resource",
    "ResourcePattern",
    "Context",
    "ModelError",
    "Permission",
    "Capability",
    "CapabilityError",
    "CapabilityStore",
    "PathScope",
    "Policy",
    "Rule",
    "PolicyEngine",
    "StaticPolicyEngine",
    "PolicyResult",
    "evaluate",
    "Effect",
    "Decision",
    "RiskAssessment",
    "Authorizer",
    "AuthorizationRequest",
    "ReplayGuard",
    "Approval",
    "ApprovalError",
    "ApprovalRequest",
    "ApprovalStore",
    "AuditError",
    "AuditEvent",
    "AuditLog",
    "AuditSink",
    "InMemoryAuditSink",
    "GuardedFilesystem",
    "GuardResult",
]
