# 03 — Capabilities (and §Least Privilege)

## Concept
A **Capability** is a single, narrow, revocable grant: "actor X may do action A within scope S,
until time T." It is the unit of authority in Renker.

## Why it exists
Coarse permissions ("the agent has filesystem access") are the root cause of agent security incidents.
A capability replaces that with the *least privilege* the task actually needs.

## Architecture
- `renker_core/capabilities/model.py`
  - `Capability(capability, scope, granted_to, granted_by, issued_at, expires_at, approval_policy,
    risk_tier, revocable, audit_required, capability_id)`.
  - `capability` is a dotted verb (`filesystem.write`); `permits_action` requires an exact match.
  - `PathScope(base)` with `permits(target)` — resolves the target and checks containment.
  - `capability_id` is derived (sha256 of the grant material) and stable.
- `renker_core/capabilities/store.py` — `CapabilityStore`: `grant`, `find(actor_urn, action)`,
  `revoke(id)`, `is_revoked(id)`. Non-revocable capabilities refuse revocation.

## §Least Privilege
Never write `"agent has filesystem access"`. Write `"agent may write to ~/Documents/drafts/**"`.
In code that means: a capability names **one** action verb and **one** path scope, is **time-bound**
(`expires_at`), and is **revocable**. Wider access = a second, separate capability, audited on its own.

## Security implications
- Exact action match prevents read→write escalation.
- Scope containment prevents target widening and traversal (see module 07).
- `expires_at` and revocation bound the blast radius in time.

## Failure modes
- Granting a scope that is too broad (e.g. `~` instead of `~/Documents/drafts`).
- Reusing one capability for multiple verbs — impossible here by design (one verb per capability).
- Naive datetimes: `issued_at`/`expires_at` must be timezone-aware or construction raises.

## Tests
`tests/test_capabilities.py` — scope inside/outside, traversal, prefix confusion, sibling, stable id,
expiry, naive-datetime rejection, dotted-verb requirement, grant/find/revoke, non-revocable refusal.

## Design trade-offs
One-verb-per-capability is slightly more verbose but makes every grant auditable and impossible to
over-broaden implicitly. Deriving the id from content makes grants deduplicable and traceable.

---

## Questions (answer before reading the reference)

**Recall**
1. Name four of the capability fields and what each constrains.
2. What does "least privilege" translate to in this code, concretely?

**Code**
3. Where is read→write escalation actually blocked — in the capability, the store, or the policy?

**Debug**
4. `Capability(...)` raises `CapabilityError: capability must be a dotted verb`. What did the caller pass?

**Security**
5. You grant `filesystem.write` on `~/Documents`. Why is that worse than `~/Documents/drafts`, and what
   attack does the narrower scope prevent?

**Architecture**
6. Why is revocation tracked in the `CapabilityStore` and not as a mutable flag on `Capability`?

--- reference ---
1. e.g. `capability` (which action), `scope` (which target), `granted_to` (which actor), `expires_at`
   (how long), `approval_policy` (auto/deny/human), `revocable` (can it be revoked).
2. One action verb + one path scope + time bound + revocable, per grant.
3. In the policy engine (`permits_action` exact match), enforced during `evaluate`. The capability
   provides the predicate; the policy applies it.
4. A capability string with no dot, e.g. `"filesystem"` instead of `"filesystem.write"`.
5. `~/Documents` lets the agent touch every document, including sensitive ones; `~/Documents/drafts`
   confines it. The narrow scope prevents "wrong target" access to files outside the working area.
6. Because `Capability` is frozen/immutable (safe to hash and reuse); revocation is mutable state about
   a grant, so it lives in the store that owns the grant lifecycle.
