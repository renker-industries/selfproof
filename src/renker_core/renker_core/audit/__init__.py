from __future__ import annotations

from renker_core.audit.log import (
    CHAIN_HASH_ALGORITHM,
    GENESIS_HASH,
    AuditError,
    AuditEvent,
    AuditLog,
    AuditSink,
    InMemoryAuditSink,
)

PRIMITIVE = "audit"

APPEND_ONLY = True

__all__ = [
    "PRIMITIVE",
    "APPEND_ONLY",
    "CHAIN_HASH_ALGORITHM",
    "GENESIS_HASH",
    "AuditError",
    "AuditEvent",
    "AuditLog",
    "AuditSink",
    "InMemoryAuditSink",
]
