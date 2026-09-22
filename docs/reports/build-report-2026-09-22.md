# Build report — 2026-09-22

Selfproof, built autonomously by a local agent under the autonomy charter. This
report says only what the evidence supports.

## Per-phase status

| Phase | Status | Evidence |
| --- | --- | --- |
| 0 Preflight | done | ADR-0001 (name), ADR-0002 (inventory) |
| 0b Scouting | partial | ADR-0003: seed adopts no external tool; candidate re-verification pending |
| 1 Seed | done | kernel imported (132 tests), ledger, CLI, CI, hooks; tag `self-host-v0` |
| 2 All gates | done | 8 gates with corpora; phase-2 report |
| 3 Adapters | done | registry + capability matrix; rules-as-data with CI drift check |
| 4 Token module | done | `selfproof bench report`; no invented numbers |
| 5 Dashboard | done | self-contained HTML + terminal; export-privacy test; craft redesign |
| — Packaging | done (desktop) | single-file binary verified on Windows; CI matrix for mac/linux |
| 6 Docs/wiki/README | done | README, explanation, reference, tutorial, wiki manifest |
| 7 Fleet | partial | read-only enumeration of both accounts; cross-repo scanning pending |
| 8 Hardening + release | done (private) | all 8 gates PASS; `release check` green; SBOM; this report |
| 9 Improvement | pending | see "Definition of done" |

## Honest metrics

- Gates: 8 of 8 PASS on the repo, **0 SKIPPED**, 0 FAIL. (`selfproof build`)
- Tests: 132 kernel + 61 Selfproof pass; ruff clean.
- Self-built share: 100% agent (every commit since the seed carries
  `Built-by: agent claude-code opus-4-8`). Human code interventions: 0.
- Autonomy rate: PRs #2–#17 were built and merged through the loop with green CI
  and no human code change. 16 merged PRs.
- Token saving: `insufficient data` (no real benchmark runs recorded yet).

## Open findings and SKIPPED checks

- Open findings (medium+): none known by the gates at the current head.
- SKIPPED required checks: none.
- Full-history secret scan and external scanner runs (gitleaks/osv/zizmor) in CI:
  not yet wired; the built-in secret/license/workflow checks pass. Tracked below.

## Every README claim, with its evidence

- "runs deterministic gates in git and CI" — the 8 gates + `.github/workflows/ci.yml`.
- "every result is bound to a commit and written to a hash-chained ledger" —
  `selfproof.core.ledger` on the kernel audit chain; `ledger verify`.
- "it builds itself" — `self-host-v0` tag; `Built-by` trailers; dashboard share.
- "8 gates, each with a corpus" — `tests/corpus/` and `tests/test_*_gate.py`.
- "zero known findings" claim form — enforced by `docs_claims`; never absolute.

## Known limitations

- `renker-core` stays proprietary until A3 (relicense) is executed.
- Server-side branch protection and secret scanning need GitHub Pro or a public
  repo; enforcement is via hooks + CI meanwhile.
- No commit signing key, so protected-path approvals cannot be signed yet;
  additive Tier B changes were merged under charter delegation.
- The holdout is created but not populated by a non-builder session, so
  overfitting-resistant improvement cycles are pending.

## Definition of done (concept section 13)

| Criterion | State |
| --- | --- |
| `v0.1.0` tagged, Phase 8 acceptance met (private) | done (this release) |
| ≥3 improvement cycles proven on the holdout, no regression | **pending** — needs the holdout populated by a non-builder session (owner step) |
| Wishes W1–W18 ticked with evidence or listed with a reason | see the phase reports and `OWNER_TODO.md` |
| Final report written | this document |

## What the owner must still do

See [`OWNER_TODO.md`](OWNER_TODO.md): A3/A4, commit signing, a fine-grained
token, populating the holdout, and (for publication) the release-readiness check
over full history with the external scanners installed.
