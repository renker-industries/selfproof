# `selfproof.adapters`

Honest declarations of how each coding agent is connected to Selfproof
(concept section 7).

- **Purpose:** record, per agent, the verified enforcement level (L0/L1/L2), the
  rules file it reads, the evidence for the level, and its limitations.
- **Boundaries:** declarations only; the actual enforcement is the git hooks and
  CI (L1) plus, where wired, an agent's native hooks (L2).
- **Must not:** claim a level the evidence does not support. An agent stays at
  the git+CI floor (L1, or L0 for a non-committing runner) until a higher level
  is wired and tested.

The capability matrix at `docs/reference/capability-matrix.md` is generated from
this registry by `scripts/gen_capability_matrix.py`.
