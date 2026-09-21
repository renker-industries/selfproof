# `selfproof` package

The Selfproof application code.

- **Purpose:** run gates over changes, record evidence on the kernel's audit
  chain, and expose it through a CLI (and later a dashboard and self-build loop).
- **Boundaries:** calls `renker_core`; never copies its logic. Adds no runtime
  dependencies.
- **Must not:** invent evidence, report a missing tool as a pass, or write to the
  ledger outside `core/runner.py`.

## Subpackages

| Path | Purpose |
| --- | --- |
| `core/` | config, evidence ledger, gate runner |
| `gates/` | the checks (seed: `language`, `proof`) |
| `cli.py` | the `selfproof` command-line interface |
