# Gate: architecture

## In one sentence
Enforces layering, acyclic imports, size budgets and dependency hygiene.

## Why it exists
Serves W3 and W5: keeps the platform small, layered and free of unreviewed
dependencies (supply-chain risk).

## What it checks
Over the `selfproof` package (kernel excluded): gate modules must not import
`selfproof.core`/`selfproof.cli`; the intra-package import graph must be
acyclic; a file may not exceed the line budget (default 400) and a function the
function-line budget (default 80); every runtime dependency in `pyproject.toml`
needs an ADR line under `docs/decisions/`.

## What blocks a change
Any violation yields `FAIL`.

## Tools and versions
Standard library only (Python 3.11+, `ast`, `tomllib`).

## Verdicts
- `PASS`: layering, cycles, budgets and dependency ADRs all clean.
- `FAIL`: at least one violation.
- `ERROR`/`SKIPPED`: not used by this gate.

## Suppressions
Adjust budgets under `[architecture]` in `selfproof.toml` with a reasoned commit;
budget changes are visible in the diff.

## Known false positives and false negatives
Function length is a coarse complexity proxy, not cyclomatic complexity. The
dependency check matches the dependency name as a substring of the ADR corpus.

## Corpus
Synthetic unit tests in `tests/test_architecture_gate.py` (cycles, budgets,
dependency/ADR pairs), since cycles and budgets cannot be expressed as files.

## Try it
```bash
selfproof build --gates architecture
```

## Evidence
Each run appends an evidence entry (`gate: architecture`).
