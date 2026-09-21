# ADR-0003: Scouting decisions (Phase 0b)

- Status: proposed (partial — live re-verification pending)
- Date: 2026-09-21
- Decider: Autopilot (charter; component replacement needs the owner)
- Wishes affected: W3, W4, W5, W6, W7, W15

## Context
Phase 0b (concept section 13) finds external repositories that strengthen
Selfproof without giving up a wish. The seed (Phase 1) deliberately adopts **no**
external tool: its `language` and `proof` gates use only the standard library
plus `pytest` and `ruff`, which are already project dev tools. So there is
nothing adopted yet that needs a corpus test or a license defence.

## Decision
1. **Seed adopts nothing external.** Zero third-party runtime dependencies; the
   kernel stays zero-dep.
2. **Candidate shortlist carried forward** for the `security` and `slop` gates in
   Phase 2, each to be re-verified (maintenance, exact license, pinned
   version+hash) and given a corpus test **before** adoption, in its own ADR:
   - `security` gate: gitleaks (MIT), osv-scanner (Apache-2.0), zizmor (MIT),
     ossf/scorecard (Apache-2.0), syft (Apache-2.0) — all orchestrated as
     external CLIs, never bundled.
   - `slop` gate: vulture (MIT, dead code), jscpd (MIT, duplication).
   - `architecture` gate: import-linter (BSD-2-Clause).
   - Sandbox candidate: anthropic-experimental/sandbox-runtime (Apache-2.0),
     Windows support alpha — evaluate, do not assume.
3. **Hard-fail respected:** Semgrep engine (LGPL-2.1) and caveman's BSL engine
   are external-CLI-only or not bundled; nothing GPL/AGPL/BSL/non-commercial
   enters the tree.

## Alternatives considered
Adopting a scouted framework now (e.g. an eval harness): deferred to the phase
that needs it, to keep the seed minimal and every adoption provable.

## Consequences
The preliminary candidate facts in concept section 13.5 are **snapshots
(unverified)** as of 2026-09-21 and must be re-verified before any depends on
them. This ADR is `proposed`, not `accepted`, until that re-verification runs.

## Evidence
Concept section 13; seed dependency set = stdlib + pytest + ruff (see
`pyproject.toml`).

## Review
Promote to `accepted` per adopted tool as Phase 2 gates land; repeat full
scouting every 10th improvement cycle.
