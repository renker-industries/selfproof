# `selfproof.gates`

The checks. Each gate returns exactly one of `PASS`, `FAIL`, `SKIPPED(reason)`,
`ERROR(reason)`. A missing tool, no network, or a timeout is never `PASS`.

- **Purpose:** detect slop and security problems and prove correctness, each gate
  backed by a known-bad / known-good corpus under `tests/corpus/`.
- **Boundaries:** gates orchestrate tools; they do not reimplement them.
- **Must not:** be weakened to make a change pass (that is a Tier C action).

| Gate | Status | Reference |
| --- | --- | --- |
| `language` | seed | `docs/reference/gates/language.md` |
| `proof` | seed | `docs/reference/gates/proof.md` |
| `slop` | phase 2 | `docs/reference/gates/slop.md` |
| `architecture` | phase 2 | `docs/reference/gates/architecture.md` |
| `test_weakening` | phase 2 | `docs/reference/gates/test_weakening.md` |
| `docs_coverage` | phase 2 | `docs/reference/gates/docs_coverage.md` |
| `docs_claims` | phase 2 | `docs/reference/gates/docs_claims.md` |
| `security` | phase 2 | `docs/reference/gates/security.md` |

Marker data for the `language` gate lives in `data/` and is excluded from the
language scan itself.
