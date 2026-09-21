# Technical overview

## Flow
```
agent → request(action, target)
      → identity (validated actor)
      → capability lookup (granted_to = actor, exact action)
      → policy evaluate (scope, expiry, revocation, approval)
      → ALLOW / DENY / REQUIRE_APPROVAL  (deterministic, explainable)
      → execute (only on ALLOW)          → audit event
      → (DENY/APPROVAL)                  → audit event, not executed
```

## Components (`renker-core`, stdlib only)
- **Identity** (`renker_core.identity`): `Actor(kind, identifier)` → urn `kind:identifier`. Validated, not
  authenticated.
- **Capabilities** (`renker_core.capabilities`): frozen `Capability` (one verb + one `PathScope`, actor-bound,
  time-bound, revocable); `CapabilityStore` (grant/find/revoke). Scope containment uses `os.path.normcase`
  path-part comparison after `resolve()` — traversal- and prefix-confusion-safe.
- **Policy** (`renker_core.policy`): `evaluate(*, actor, action, target, store, now=None) -> PolicyResult`.
  Pure, deterministic, explainable; fails closed.
- **Audit** (`renker_core.audit`): `AuditLog` with sha256 hash chain + atomic head anchor + `verify()` +
  read-only `query()`; thread-safe, `fsync`ed.
- **Integration** (`renker_core.integration`): `GuardedFilesystem` runs the whole pipeline on a real file
  read/write.

## Security model (summary)
- Decision inputs are trusted grants only; the request cannot inject authorization or risk.
- Least privilege by construction (one action + one scope per capability; immutable).
- Tamper-evident audit (not "immutable").
- Honest non-guarantees: identity is not authentication; audit has a crash window and no multi-process lock;
  enforcement applies only to actions routed through the guard. Full detail: `docs/THREAT_MODEL.md`.

## Performance (measured, single core, warm; see `benchmarks/bench.py`)
- identity creation ≈ 0.7 µs; policy evaluate ≈ 0.7 ms (dominated by filesystem path canonicalization, a
  deliberate security-over-speed choice); audit append ≈ 12.5 ms with `fsync` durability.

## Integration
`rencora` consumes core via an optional, lazy adapter that is off by default and fails closed on
misconfiguration; the shipped build is unaffected when core is absent.
