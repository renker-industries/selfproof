# ADR-0001: Project name is "Selfproof"

- Status: accepted
- Date: 2026-09-21
- Decider: Autopilot (charter authorization; owner confirmed the working name)
- Wishes affected: W5, W9

## Context
The concept sets the working name "Selfproof" and requires a collision check as
the first Phase 0 task (concept sections 11 and 15). A direct collision means
the name is not used; the fallback is "Proofsmith".

## Decision
Use **Selfproof**. Home: `github.com/renker-industries/selfproof` (monorepo).

## Alternatives considered
- **Proofsmith** (fallback): PyPI `proofsmith` is free (HTTP 404) but the concept
  notes it sits next to many `proof-*` repos; kept only as a fallback.
- **Castellum, Praesidium, Bulwark, Proofloop, Plumbline**: rejected in the
  concept because each collides with existing security/AI projects or companies.

## Consequences
Good: descriptive, available across the registries checked. Bad/residual risk:
a **trademark** search was not performed; common-law or registered marks may
exist. Recorded in `docs/reports/OWNER_TODO.md`.

## Evidence
Collision checks run 2026-09-21 with `curl`/`gh`:

| Namespace | Query | Result |
| --- | --- | --- |
| PyPI | `pypi.org/pypi/selfproof/json` | HTTP 404 (available) |
| npm | `registry.npmjs.org/selfproof` | HTTP 404 (available) |
| GitHub repos | `search/repositories?q=selfproof in:name` | `total_count` = 0 |
| GitHub user/org | `users/selfproof` | HTTP 404 (available) |

## Review
Re-check before publication (charter A4): re-run the registry checks and add a
trademark search result.
