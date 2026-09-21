# Status

- Generated: 2026-09-21 (build session)
- Stage: `self-hosted` (cutover tag `self-host-v0`)
- Phase: 5 (Dashboard) done. Phases 0-5 complete. Next: Phase 6 (docs/wiki/
  README), Phase 7 (fleet mode), Phase 8 (hardening + release v0.1.0).
- Mode: full autopilot; A3 (relicense) and A4 (publish) gated at execution.
- Merged PRs through the loop: #2-#11 (plus the seed). 56 selfproof tests +
  132 kernel tests pass; ruff clean; 7 gates PASS + security SKIPPED.

## Done (with evidence)
- **Phase 0/0b**: environment, inventory (ADR-0002), name check (ADR-0001),
  scouting (ADR-0003). Concept SHA-256 in the charter.
- **Phase 1 (Seed)**: private repo, kernel imported with history (132 tests
  green), ledger on the audit chain, CLI, CI, hooks, docs skeleton. Cutover
  proven (PR #1 blocked), tag `self-host-v0`. Holdout repo created (A9).
- **Phase 2 (All gates)**: all eight gates exist with corpora/tests and
  references, each merged through the self-hosted loop with green CI:
  `language`, `proof` (seed); `slop`, `architecture`, `test_weakening` (PR #3);
  `docs_coverage`, `docs_claims` (PR #4); `security` (PR #5).
  - Local run: 7 gates PASS, `security` SKIPPED (external scanners not installed
    — honest, not a pass). 38 Selfproof tests + 132 kernel tests pass; ruff clean.

## Done since (Phases 3-5)
- Phase 3: adapter registry + honest capability matrix (PR #7); rules-as-data
  `rules/agents.yaml` generating `CLAUDE.md`/`AGENTS.md`/`GEMINI.md` with a CI
  drift check (`selfproof rules check`, PR #9).
- Phase 4: token module — net-saving measurement + `selfproof bench report`;
  no invented numbers, `insufficient data` below n=5 (PR #10).
- Phase 5: dashboard — self-contained HTML export + terminal summary, reads
  only the ledger/git/benchmarks, export-privacy test (PR #11).

## Next (Phase 6-8)
- Phase 6: the wiki source set, README quickstart/comparison, explanation pages;
  pass docs_coverage/docs_claims/readability.
- Phase 7: fleet mode — scan both GitHub accounts; findings count only with
  before+after entries.
- Phase 8: install the external security scanners (turn `security` from SKIPPED
  to PASS), SBOM/provenance, Scorecard, release `v0.1.0` (private; public only
  if A4 + readiness check pass).

## Blocked (by design or plan)
- A3/A4 wait for a live owner OK.
- Server-side branch protection + secret scanning need GitHub Pro or A4
  (free-plan limit); enforcement is via hooks + CI meanwhile.
- Signed protected-path approvals wait on a signing key (OWNER_TODO); additive
  Tier B changes merge under charter delegation until then.

## Metrics snapshot
- Gates: 8 of 8 implemented. Kernel tests 132, Selfproof tests 38, ruff clean.
- Self-built share: every commit since the seed carries
  `Built-by: agent claude-code opus-4-8`; PRs #2–#5 built and merged by the loop.
- `security`: SKIPPED pending gitleaks/osv-scanner/zizmor (Phase 8).

## Next three tasks
1. Phase 3: the git adapter formalized (L1) + the adapter interface + capability matrix.
2. Claude Code adapter (L2 target, ported from CUSTOS) with honest evidence.
3. Codex / Gemini CLI adapters (verify capabilities from current docs first).

## Chain head
Ledger is machine-local (gitignored); head is anchored at each release tag.
