# PERFECTION_AUDIT

- **Date:** 2026-08-10
- **Basis:** direct inspection of the current code (`git @ d464ca1`), not prior summaries. Test/lint results
  are from an actual run (renker-core: ruff clean, 71 passed; rencora guard: 13 passed; CI green).
- **Scope:** the `renker-core` authorization slice and its opt-in `rencora` wiring. `renkervault` and
  `continuum` are reviewed only for boundary/coupling.

Status legend: **IMPLEMENTED · TESTED · PARTIAL · EXPERIMENTAL · DOCUMENTED-ONLY · PLANNED · BROKEN**

## Component status (ground truth)

| Component | File | Status | Notes |
|---|---|---|---|
| Identity (`Actor`, urn) | `identity/actor.py` | IMPLEMENTED + TESTED | validated, control/whitespace rejected; not authentication |
| Capability model | `capabilities/model.py` | IMPLEMENTED + TESTED | frozen, one verb + one scope, derived id, expiry |
| Path scope | `capabilities/model.py` | IMPLEMENTED + TESTED | normcase containment, traversal/prefix-safe, 400-example property test |
| Capability store | `capabilities/store.py` | IMPLEMENTED + TESTED | grant/find/revoke; non-revocable refuses |
| Policy engine | `policy/engine.py` | IMPLEMENTED + TESTED | deterministic, explainable, ALLOW/DENY/REQUIRE_APPROVAL |
| Audit log | `audit/log.py` | IMPLEMENTED + TESTED | sha256 chain + head anchor + verify; thread-safe; fsync; atomic anchor |
| Integration guard | `integration/filesystem.py` | IMPLEMENTED + TESTED | real file I/O through the pipeline |
| rencora opt-in wiring | rencora `core/renker_guard.py`, `actions/file_controller.py` | IMPLEMENTED + TESTED | off by default, fail-closed on bad config |
| crypto_interface | `crypto_interface/__init__.py` | IMPLEMENTED (interfaces only) | no crypto; Protocols only |
| memory/tasks/events/experiments/evidence/protocol | `*/__init__.py` | PLANNED (placeholders) | intentionally not built |
| Audit query API | — | PLANNED | **gap** — being added this phase |
| Public API export contract | — | PARTIAL | submodule `__all__` present; no top-level surface test |
| Versioning policy | — | DOCUMENTED-ONLY | `__version__="0.0.1"`; no policy doc |

## Architecture
- **Boundaries:** clean. `renker-core` is stdlib-only, zero runtime dependencies. Dependency direction is
  correct: consumers (rencora) → core; core depends on nothing product-specific.
- **Coupling / cycles:** none found. Submodule imports are one-directional (policy→capabilities→identity;
  integration→all; no cycles).
- **Duplication:** `RISK_TIERS` is defined in both `policy/__init__.py` and `capabilities/model.py` — minor,
  acceptable as a shared vocabulary constant, but worth a single source of truth (LOW).
- **Unnecessary abstractions:** none egregious. The six placeholder primitives are documented as PLANNED,
  not speculative code.
- **Unstable interfaces:** the public API is not yet explicitly frozen at the package top level (MEDIUM).

## Security
- **Identity:** validated naming, not authentication (documented). Spoofing a *trusted* actor is out of
  scope and stated in the threat model.
- **Authorization / capabilities / policy:** the decision derives **only** from trusted grants in the store
  plus actor/action/target. `evaluate()` has **no `context` or risk parameter** — a request cannot inject
  its own `riskTier`/`authorized` flag. This is a real strength; it needs explicit regression tests (added).
- **Path handling:** normcase-normalized `parts` containment after `resolve()`; traversal, prefix confusion,
  case tricks, and empty/None targets covered. Symlink/junction escape is handled by `resolve()` but not yet
  explicitly tested on Windows (privilege-gated) — MEDIUM.
- **Process execution / secrets / sandboxing:** not in core scope. rencora owns process/secret handling
  (DPAPI, tool-risk gate); core only guards file actions routed through the guard.
- **Audit integrity:** tamper-evident hash chain + head anchor + `verify()`; thread-safe; atomic anchor.
  Honest non-guarantees documented (crash window, multi-process, both-file rewrite).
- **Serialization/deserialization:** audit uses canonical JSON; corrupt lines raise `AuditError`. Capability
  serialization to/from a wire format is **not** implemented — PLANNED (needed before cross-process use).
- **Trust boundary / prompt injection / confused deputy:** the boundary is outside the LLM by construction
  (the engine ignores the request's claims). Dedicated adversarial suites added this phase.
- **Privilege escalation:** exact action match + scope containment + actor binding prevent read→write and
  cross-actor use. Tested.

## Reliability
- **Error handling:** safe defaults (DENY / return False) on malformed input; execution errors are audited
  as `outcome="error"` and not silently swallowed.
- **Race conditions:** audit `record()` is locked (thread-safe within a process). `CapabilityStore` mutation
  (grant/revoke) is **not** locked — acceptable because grants are configured, not concurrently mutated, but
  documented (LOW).
- **Partial failure / corruption:** audit detects corruption/tamper; a crash between append and anchor is
  detected (not silently accepted). Documented.
- **Timeouts/retries:** not applicable to core (rencora owns tool timeouts).

## Testing
- 71 renker-core tests: unit, adversarial, property (hypothesis, 400 + 150 examples), concurrency,
  regulated acceptance. 13 rencora guard tests (skip without core). CI runs ruff + pytest.
- **Gaps:** no audit-query tests (feature missing), no explicit prompt-injection/confused-deputy suite
  (behavior present, tests implicit), no public-API contract test, no performance baseline, no dependency
  audit / build step in CI.

## Developer Experience
- Install: `pip install -e ".[dev]"`; demo: `python demo/demo_slice.py` (works from clean env).
- CI: ruff + pytest. No build/package or dependency-audit gate yet (MEDIUM).
- Docs: vision, threat model, attack catalog, learning curriculum, ADR-0001. No developer `examples/` folder,
  no marketing/positioning, no comparison to alternatives (targets of this phase).
- Error messages: policy denials are explainable (actor/action/target/allowed scope/reason). Good.

## Product
- **Demonstrable today:** the ALLOW/DENY file-guard flow with a verifiable audit trail; regulated isolation
  scenarios (hospital/law-firm) as tests; opt-in enforcement inside rencora's real file writes.
- **Infrastructure only:** the six placeholder primitives; crypto interfaces.
- **Sellable angle:** "capability + policy + tamper-evident audit for autonomous agent file actions,
  enforcement outside the LLM" — narrow but real and honest.
- **Too speculative to sell now:** memory/experiments/evidence, RencoraLM, Continuum research claims.

---

## Priority matrix (this phase)

| Priority | Item |
|---|---|
| **CRITICAL** | Regression tests proving the request cannot set risk/authorization (trust boundary); prompt-injection + confused-deputy suites; fail-closed on unknown action (verify) |
| **HIGH** | Audit query API (read-only, integrity-preserving) + tests; public-API surface + contract test; ADRs for capability/policy/audit/dependency-direction |
| **MEDIUM** | Versioning policy doc; developer `examples/protected_agent/`; performance baseline; CI build + dependency-audit gate; marketing docs with honest `claims.md`; comparison-to-alternatives doc |
| **LOW** | De-duplicate `RISK_TIERS`; document store-mutation concurrency; Windows symlink test (privilege-gated) |
| **DEFER** | Capability wire serialization; memory/tasks/events/experiments/evidence; multi-process audit locking; signed identities; bundling core into the shipped rencora exe (Option B) |

The guiding rule for the rest of the phase: **fix foundational trust/security first, then close the query/API
gaps, then documentation/DX/marketing — no speculative features.**
