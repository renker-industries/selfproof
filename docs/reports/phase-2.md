# Phase 2 report: All gates

- Date: 2026-09-21
- Result: **done**

## What was built
All eight gates from concept section 5, each with a known-bad / known-good
corpus (or synthetic unit tests where a file corpus cannot express the check),
tests, and a generated-from-template reference page:

| Gate | Kind | Verdict on repo | PR |
| --- | --- | --- | --- |
| `language` | text | PASS | seed |
| `proof` | orchestration | PASS | seed |
| `slop` | AST/text | PASS | #3 |
| `architecture` | AST/graph | PASS | #3 |
| `test_weakening` | diff | PASS | #3 |
| `docs_coverage` | fs/AST | PASS | #4 |
| `docs_claims` | text | PASS | #4 |
| `security` | scan + external | SKIPPED | #5 |

## Evidence
- Every gate's corpus is asserted by a test (`tests/test_*_gate.py`); CI runs
  them on every PR. Deliberately-bad corpus examples are caught; known-good
  examples are not flagged.
- The cutover (`self-host-v0`) already proved a bad change is blocked in CI.
- `security` reports `SKIPPED` because gitleaks/osv-scanner/zizmor are not
  installed; a missing tool is never reported as a pass (concept 4.1).

## Wishes ticked (with evidence)
- **W3** (slop-free, protected): `slop`, `architecture` gates + corpora.
- **W5** (secure repo): `security` gate (built-ins) + repo hardening applied
  where the plan allows.
- **W8** (honesty): `docs_claims` gate; `security` SKIPPED not faked.
- **W11/W17** (documented, English): `docs_coverage`, `language`, gate references.

## Not done / carried forward
- External security scanners (Phase 8) to turn `security` from SKIPPED to PASS.
- "Deliberately weakened gate turns CI red" is covered by `test_weakening` +
  corpora; a dedicated mutation demo is a Phase 9 improvement item.

## Human interventions
None in Phase 2. All five PRs (#2–#5 plus the seed) built and merged by the loop
with green CI. Protected-path (Tier B) gate additions merged under charter
delegation because commit signing is unavailable (tracked in OWNER_TODO).
