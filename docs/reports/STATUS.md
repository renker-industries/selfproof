# Status

- Generated: 2026-09-21 (build session)
- Stage: `self-hosted` (cutover tag `self-host-v0`)
- Phase: 1 (Seed) — complete; entering Phase 2
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

## Done since (Phase 1 completion)
- Private repo `renker-industries/selfproof` created and seed pushed; seed CI green.
- Hardening applied where the plan allows: workflow token read-only, Dependabot
  alerts + automated fixes on. Branch protection, rulesets and secret scanning
  are **blocked by the free plan for a private repo** (see OWNER_TODO);
  enforcement relies on hooks + red CI until publication or a plan upgrade.
- Cutover done: PR #1 (deliberately-bad German file) was blocked by the language
  gate in CI; PR closed unmerged; tag `self-host-v0` pushed.
- Private holdout repo `renker-industries/selfproof-holdout` (A9) created with
  the anti-gaming contract.

## Blocked
- A3/A4 wait for a live owner OK (by design).
- Server-side branch protection / secret scanning wait on plan or A4.

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
