# ADR 0006 — Decision-centric kernel; Effect enum vs. rich Decision

- **Status:** Accepted
- **Date:** 2026-08-11

## Context
renker-core evolved from a string-based `evaluate(actor, action:str, target:str)` into a security decision
kernel with strong types and a first-class, immutable, serializable `Decision`. Previously the public name
`Decision` referred to the effect **enum** (`ALLOW`/`DENY`/`REQUIRE_APPROVAL`), which is also mirrored in the
shipped public package `renker-core-authz`.

## Decision
- Introduce **`Effect`** as the canonical enum (`ALLOW`/`DENY`/`REQUIRE_APPROVAL`).
- Make the public **`Decision`** the rich record: `decision_id, effect, subject, action, resource, policy_id,
  policy_version, reason, obligations, timestamp` (immutable, `to_dict`/`from_dict`).
- Keep a backward-compat alias `Decision = Effect` **inside `renker_core.policy.engine`**, so the legacy
  `from renker_core.policy import Decision` and `PolicyResult.decision` (an `Effect`) keep working and the
  existing test suite stays green. The old string-based `evaluate` and `GuardedFilesystem` are retained.
- Reuse the existing `Capability`/`CapabilityStore`/`PathScope` and hash-chain `AuditLog` rather than
  re-inventing them; the new `Action`/`Resource`/`Identity` types map onto them at the boundary.

## Why (conflict resolution)
The task requires `Decision` to be the rich object and `Effect` the enum. Keeping `Decision` as the enum would
block that; renaming the enum everywhere would break the existing green suite and diverge further from the
shipped `renker-core-authz`. The alias localizes the compatibility cost to one module while giving the public
API the intended shape. The public breaking change (`renker_core.Decision` now means the rich record) is
deliberate and versioned as **0.2.0**.

## Consequences
- Clean, typed, Decision-centric public API; 132 tests green; mypy/ruff clean.
- `renker-core` (private, evolving) now diverges more from `renker-core-authz` (public, shipped, black-box
  verified in `RENCORA.exe`). That package remains the source of truth for the *shipped* enforcement; this
  kernel is the next generation intended to re-supersede it after review. Tracked as platform tech-debt.
- Audit gained optional `resource`/`decision_id` fields (backward-compatible, defaulted) so decisions are
  fully traceable; the legacy `AuditLog` record API is unchanged for existing callers.
