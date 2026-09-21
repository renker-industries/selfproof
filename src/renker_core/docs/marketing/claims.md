# Claims — what we can and cannot say

Every claim is tagged. **VERIFIED** = backed by code + a passing test in this repo. **UNVERIFIED** = plausible
but not yet demonstrated/measured here. **FUTURE** = intended, not built. Marketing may use VERIFIED claims
as-is; UNVERIFIED/FUTURE must be labeled as such.

Banned words unless objectively justified: *unhackable, guaranteed secure, military-grade, AGI, revolutionary*.
We do not use them.

## VERIFIED (code + passing test)
- The security decision is deterministic and does not use the request's claims — `evaluate` has no
  context/risk/authorization input. *(test_trust_boundary.py)*
- Capabilities are immutable; scope, actor, action, and risk tier cannot be changed after issuance.
  *(test_trust_boundary.py)*
- Path scope resists traversal, prefix confusion, and case tricks; a 400-example property test cross-checks it
  against ground truth. *(test_properties.py, test_hardening.py)*
- Expired and revoked capabilities are denied; one actor cannot use another's capability. *(test_security_attacks.py)*
- Every allow/deny produces an audit event; the hash chain + head anchor detect modification, insertion,
  reordering, tail truncation, and full deletion; a 150-example fuzz test detects every single-byte mutation.
  *(test_audit.py, test_hardening.py, test_properties.py)*
- The system fails closed on unknown actions, malformed input, and (in rencora) malformed config.
  *(test_trust_boundary.py, rencora test_file_controller_guard.py)*
- Real rencora file **write, read, and delete** can be routed through the guard, opt-in and off by default,
  without changing default behavior. *(rencora test_file_controller_guard.py, test_filesystem_security.py still green)*
- Zero runtime dependencies; 93 renker-core tests + 16 rencora guard tests pass; CI is green.
- The authorization engine is published as a standalone **public, Apache-2.0, zero-dependency** package,
  `renker-core-authz` (89 tests, CI green), and rencora's enforcement works with **only** that public package
  installed. *(renker-core-authz CI; rencora guard tests against the public package)*
- **`renker-core-authz` is enforced in the shipped `RENCORA.exe`.** The full binary, built on CI via the
  app's own `main.spec` in an environment proven to have the public package and **no** private `renker_core`,
  passes a 12/12 black-box matrix: allow/deny for write/read/delete; traversal/outside/wrong-actor denied;
  denied read does not leak file content; 8 audit events present and the chain verifies; malformed config
  fails closed. *(CI run 31486004843; rencora `verification/EXE_ENFORCEMENT_REPORT.md`)*

## UNVERIFIED (not demonstrated/measured here)
- Performance figures beyond the single-machine micro-benchmark in `benchmarks/bench.py` (no multi-core,
  no sustained-load, no cross-OS numbers).
- Behavior under real adversarial red-teaming by a third party (only our own adversarial tests exist).
- Windows symlink/junction escape resistance (handled by `resolve()` but not tested under privilege).
- Suitability for any specific compliance regime (HIPAA/GDPR/SOC2) — not assessed.

## FUTURE (intended, not built)
- Cryptographic authentication of actors (signed identities).
- Capability **expiry** exposed through the rencora config (the config→capability mapping does not yet wire
  `expires_at`; expiry is engine-verified only).
- Capability wire serialization and cross-process/cross-language use via `protocol`.
- Guarding actions beyond file write/read/delete (move/copy/rename, process, network).
- External anchoring/notarization of the audit chain; multi-process audit coordination.
- Any external security audit or certification.

## Do not claim
- "Immutable audit log" → say **tamper-evident**.
- "Stops prompt injection" → say **prevents injection from becoming an unauthorized action, for guarded actions**.
- "Production-ready for hospitals/courts" → say **a tested vertical slice with documented limits; not
  externally audited**.
