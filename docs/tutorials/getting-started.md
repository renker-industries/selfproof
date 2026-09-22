# Getting started (five minutes)

## In one sentence
Run the gates, read the evidence, open the dashboard.

## Before you begin
Python 3.11+ and git. From the repository root, put the source on the path:

```bash
export PYTHONPATH=src:src/renker_core   # Windows: set to "src;src/renker_core"
```

Or use the packaged binary, which needs neither (see
[running as an app](../guides/desktop.md)).

## 1. Run the gates
```bash
python -m selfproof.cli build
```
Each gate prints its verdict. A `SKIPPED` line means a tool was missing — that is
not a pass.

## 2. Verify the evidence
```bash
python -m selfproof.cli ledger verify
```
This recomputes the hash chain and prints the current head.

## 3. See the dashboard
```bash
python -m selfproof.cli dashboard open
```
It opens a self-contained page with the checks recorded, what was prevented, the
self-built share and the token saving.

## What you just proved
The gates ran against your exact commit and left verifiable evidence. Nothing
here claims more than the checks that actually ran.

## Next
- [How self-building works](../explanation/how-self-building-works.md)
- [What Selfproof proves](../explanation/what-selfproof-proves.md)
- [Configuration reference](../reference/config.md)
