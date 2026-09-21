# Versioning policy — renker-core

renker-core follows **Semantic Versioning** (`MAJOR.MINOR.PATCH`). The current version is `0.1.0`.

## What the public API is
Only the names exported in `renker_core.__all__` are public API:

`Actor`, `IdentityError`, `Capability`, `CapabilityError`, `PathScope`, `CapabilityStore`, `Decision`,
`PolicyResult`, `evaluate`, `AuditLog`, `AuditEvent`, `AuditError`, `GuardedFilesystem`, `GuardResult`,
`__version__`, `PRIMITIVES`.

Everything else (submodule internals, private helpers) is implementation detail and may change at any time.
A contract test (`tests/test_public_api.py`) fails if the surface drifts unintentionally.

## What each bump means
- **MAJOR** — a breaking change to the public API or to a **security guarantee** (e.g. changing what
  `evaluate` treats as ALLOW, or the audit hash scheme). Security-relevant breaks always bump MAJOR.
- **MINOR** — backward-compatible additions (new public function, new optional parameter with a safe default,
  new audit query filter).
- **PATCH** — backward-compatible fixes with no API change.

## Pre-1.0 note
While on `0.x`, the API is stabilizing and MINOR may still contain breaking changes if a security defect
requires it — such breaks will be called out explicitly in the changelog and the Phase report.

## Consumer expectations
`rencora` consumes core through an optional adapter. When core is later pinned as a real dependency, it must
pin a compatible range (e.g. `>=0.1,<0.2`) so a MAJOR bump never silently breaks the product. The audit hash
scheme and the canonical serialization are part of the compatibility contract: changing them is a MAJOR event
and requires a documented migration for existing logs.
