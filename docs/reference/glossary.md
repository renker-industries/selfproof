# Glossary

- **Gate** — a deterministic check that returns exactly one verdict and writes a
  ledger entry.
- **Verdict** — one of `PASS`, `FAIL`, `SKIPPED(reason)`, `ERROR(reason)`. A
  missing tool is never a pass.
- **Ledger** — the append-only, hash-chained record of every check, built on the
  kernel's audit chain. `selfproof ledger verify` recomputes it.
- **Corpus** — known-bad and known-good examples that test a gate itself.
- **Protected path** — a path (the gates, the kernel, the rules, CI, the license,
  the charter) whose change needs a signed human approval.
- **Tier A / B / C** — merge policy: A merges when proofs pass; B needs an
  approval; C is refused (weakening a check, editing the ledger, forging an
  approval).
- **Capability level** — how strongly an adapter enforces the rules: L0 advisory,
  L1 git+CI, L2 native session hooks.
- **Self-built share** — the share of commits and lines written by the agent
  versus a human, seed included, failures shown.
- **Cutover** — the moment CI first ran the platform on a PR and blocked a bad
  change; anchored by the `self-host-v0` tag.
- **Holdout** — a private corpus the builder never reads; only aggregate scores
  leave it, to reduce overfitting.
