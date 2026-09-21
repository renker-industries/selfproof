# `selfproof.core`

Configuration, the evidence ledger, and the gate runner.

- **Purpose:** provide the shared machinery every gate and command relies on.
- **Boundaries:** the ledger is the single source of truth for evidence; it is
  built on `renker_core.AuditLog`, not a second format.
- **Must not:** define a competing evidence store, or record evidence from
  anywhere but `runner.run_gates`.

| Module | Purpose |
| --- | --- |
| `config.py` | load `selfproof.toml` over defaults (stdlib TOML, zero deps) |
| `ledger.py` | append-only, hash-chained evidence over the kernel audit chain |
| `runner.py` | run gates, hash output, append one evidence entry per gate |
