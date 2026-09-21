# ADR 0002 — Capabilities are immutable, revocation is external

- **Status:** Accepted
- **Date:** 2026-08-10

## Context
A capability grants an actor a specific, scoped, time-bound authority. If a capability object could be
mutated after issuance, an attacker (or a bug) could widen its scope, change its actor, or downgrade its
risk tier after the fact — silently defeating least privilege.

## Decision
`Capability` is a **frozen** dataclass. Its `capability_id` is derived from its content (sha256 of the
grant material). It is never modified in place. Revocation and expiry are handled **outside** the object:
- expiry via `expires_at` compared to UTC now,
- revocation via a `CapabilityStore` that tracks revoked ids (and refuses to revoke non-revocable grants).

## Consequences
- A capability's scope, actor, action, and risk tier cannot silently change (enforced by `FrozenInstanceError`,
  tested in `test_trust_boundary.py`).
- To change authority you must issue a new capability and/or revoke the old one — an explicit, auditable act.
- The store, not the object, owns mutable lifecycle state; store mutation is not concurrency-locked (grants
  are configured, not concurrently mutated) — documented as a known limitation.
