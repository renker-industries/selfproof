# ADR-0002: Inventory and classification of the owner's assets

- Status: accepted
- Date: 2026-09-21
- Decider: Autopilot (charter)
- Wishes affected: W1, W14, W15

## Context
Phase 0 requires an inventory of everything the owner has on the topic, each
item classified as `kernel`, `module`, `reference`, `fleet-target` or `excluded`
with a written reason. Nothing is dropped silently (concept section 3).

## Decision
Source: `gh repo list` for both accounts on 2026-09-21 (private included) plus
the concept's source table. Classification:

| Repo (owner) | Vis. | Class | Reason |
| --- | --- | --- | --- |
| `sebastianrenker/renker-core` | public | **kernel** | dependency-free decision kernel; 132 tests; imported with history (A2) |
| `sebastianrenker/renker-core-authz` | public | **reference** | Apache-2.0 predecessor; port missing features into renker-core, then archive |
| `renker-industries/custos` | public | **module** | MIT gate engine, fleet mode, seed builder, dashboard look; split into neutral core + Claude adapter |
| `sebastianrenker/renker-flint` | private | **module** | token-saving layer (RENKER FLINT) for the token module |
| `sebastianrenker/continuum` | public | **reference** | MIT verification-layer idea flows into `docs_claims`/`proof`; materials code stays out |
| `sebastianrenker/rencora` | private | **fleet-target** | personal, non-commercial assistant; first real-world fleet test; never vendored |
| `sebastianrenker/rencora-public` | public | **fleet-target** | public variant of rencora |
| `sebastianrenker/renkervault` | public | **fleet-target** | zero-knowledge chat prototype; not part of v0.1 |
| `sebastianrenker/renker-swarm` | public | **fleet-target** | multi-provider agent orchestrator; scan target once stable |
| `sebastianrenker/sebastianrenker.github.io` | public | **reference** | becomes the project site; claims go through `docs_claims` |
| `sebastianrenker/renker-whitepaper` | public | **reference** | topic documentation |
| `sebastianrenker/renker-agent-demo` | public | **reference** | demo material |
| `sebastianrenker/paper-bot` | private | **excluded** | paper-trading finance bot; off-topic, hard safety constraints |
| `sebastianrenker/memecoin-bot` | private | **excluded** | memecoin analysis tool; off-topic, hard safety constraints |
| `sebastianrenker/STYLEAI` | private | **excluded** | fashion app; off-topic (possible future fleet target) |
| `sebastianrenker/aegis-suit-studio` | private | **excluded** | exosuit digital twin; off-topic |
| `sebastianrenker/energiereaktor-explorer` | private | **excluded** | energy explorer; off-topic |
| `sebastianrenker/sebastianrenker` | public | **excluded** | GitHub profile README |

## Alternatives considered
Importing more repos into the monorepo now: rejected. Only `renker-core` is a
kernel; the rest are orchestrated (modules), referenced, or scanned (fleet), so
they stay in their own repos to avoid coupling.

## Consequences
Excluded repos remain fleet-scan candidates in Phase 7 if code and topic fit.
Reclassification is a new ADR.

## Evidence
`gh repo list sebastianrenker --limit 200` and `gh repo list renker-industries`
outputs captured in the build session on 2026-09-21.

## Review
Re-run the inventory at the start of Phase 7 (fleet mode) and every 10th
improvement cycle.
