from __future__ import annotations

import re

import renker_core

EXPECTED_PUBLIC_API = {
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
}


def test_all_declares_expected_surface():
    assert set(renker_core.__all__) == EXPECTED_PUBLIC_API


def test_every_public_name_is_importable():
    for name in renker_core.__all__:
        assert hasattr(renker_core, name), name


def test_version_is_semver():
    assert re.fullmatch(r"\d+\.\d+\.\d+", renker_core.__version__)


def test_target_import_shape_works():
    from renker_core import (  # noqa: F401
        Action,
        Authorizer,
        Capability,
        Decision,
        Identity,
        Policy,
        Resource,
    )
