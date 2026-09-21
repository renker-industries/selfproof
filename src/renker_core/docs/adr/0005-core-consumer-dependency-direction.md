# ADR 0005 — Dependency direction: consumers depend on core, never the reverse

- **Status:** Accepted
- **Date:** 2026-08-10

## Context
The platform has a private foundation (`renker-core`) and public products (`rencora`, `renkervault`,
`continuum`). If core depended on a product, or a product coupled tightly to core internals, the foundation
would stop being reusable and releases would block each other.

## Decision
- `renker-core` depends on **nothing product-specific** and has **zero runtime dependencies** (stdlib only).
- Products depend on core, not the reverse. Today `rencora` consumes core through an **optional, lazy**
  adapter (`core/renker_guard.py`) that degrades to a no-op when core is absent, so rencora's public CI and
  shipped build are unaffected.
- Cross-language consumers (renkervault, TS/Tauri) integrate through a wire `protocol` (planned), not by
  importing Python internals.
- Only the names in `renker_core.__all__` are public API; everything else is internal.

## Consequences
- Core stays small, auditable, and independently testable.
- **Option B is now implemented.** The authorization engine (identity, capabilities, policy, audit,
  integration) is published as a standalone **public, Apache-2.0** package
  [`renker-core-authz`](https://github.com/sebastianrenker/renker-core-authz), zero-dependency. rencora
  prefers it (falling back to private `renker_core` for dev) and lists it in `requirements.txt` +
  `main.spec`, so a build can bundle it and enforce. Proven: rencora's guard tests pass with **only** the
  public package installed (private `renker_core` absent).
- **Source-of-truth note:** the enforcement modules currently exist in both private `renker-core` and public
  `renker-core-authz`. To avoid drift, the public package is the canonical **public** home; a follow-up should
  make private `renker-core` re-export from it rather than keep a parallel copy. Until then, changes to the
  authz primitives must be mirrored (tracked in the Phase report / technical debt).
