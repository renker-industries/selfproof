# Status

- Generated: 2026-09-21 (build session)
- Stage: `seed`
- Phase: 1 (Seed) — in progress
- Mode: full autopilot; A3 (relicense) and A4 (publish) gated at execution.

## Done (with evidence)
- Phase 0 preflight: environment verified (git 2.54, gh as `sebastianrenker`,
  Python 3.11+3.12, signing: none). Concept SHA-256 recorded in the charter.
- Phase 0 inventory: ADR-0002 (all repos of both accounts classified).
- Phase 0 name check: ADR-0001 (PyPI/npm/GitHub clear for "selfproof").
- Phase 0b scouting: ADR-0003 (seed adopts no external tool; candidates
  shortlisted for Phase 2, re-verification pending).
- Kernel import: `renker-core` imported with history into `src/renker_core/`;
  132 kernel tests green, unchanged.
- Seed code: evidence ledger on the kernel audit chain; `language` and `proof`
  gates with corpora; `selfproof` CLI. 11 Selfproof tests + 132 kernel tests
  pass locally; ruff clean.
- Docs skeleton, PR/issue templates, CODEOWNERS, CONTRIBUTING, CHANGELOG, CI
  (verify-only), git hooks.

## Partial / next
- Create the private repo `renker-industries/selfproof` and push the seed.
- Apply repository hardening (branch protection, secret scanning) — some steps
  are owner-manual (see OWNER_TODO).
- Cutover: land a deliberately-bad PR and confirm CI blocks it → tag
  `self-host-v0`.
- Create the private holdout repo `renker-industries/selfproof-holdout` (A9).

## Blocked
- A3/A4 wait for a live owner OK (by design).

## Metrics snapshot
- Kernel tests: 132 passed. Selfproof tests: 11 passed. ruff: clean.
- Gates implemented: 2 of 8 (`language`, `proof`).
- Self-built share: seed commits carry `Built-by: agent claude-code opus-4-8`.

## Next three tasks
1. Push seed to the private repo and harden settings.
2. Execute the cutover (bad-PR-blocked) and tag `self-host-v0`.
3. Open Phase 2 backlog issues (remaining six gates), begin with `slop`.

## Chain head
Ledger is machine-local (gitignored); head is anchored at each release tag.
