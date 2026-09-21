# Gate: docs_coverage

## In one sentence
Checks that required documentation exists and is structurally complete.

## Why it exists
Serves W11 and W17 and the documentation standard (concept 10.2): nothing exists
that is not documented.

## What it checks
Over `src/selfproof` (kernel excluded): every module has a module docstring;
every public top-level function and class has a docstring; every directory with
Python files has a `README.md`; every gate class has a reference page under
`docs/reference/gates/`; and the generated CLI reference `docs/reference/cli.md`
exists.

## What blocks a change
Any missing item yields `FAIL`.

## Tools and versions
Standard library only (`ast`, `pathlib`).

## Verdicts
- `PASS`: all checked items are present.
- `FAIL`: at least one gap.
- `ERROR`/`SKIPPED`: not used.

## Suppressions
None by config; write the missing documentation instead.

## Known false positives and false negatives
Presence and structure only, not quality (concept's honest limit). Docstring
coverage is checked for modules, public top-level functions and public classes;
methods are covered by their class. Changelog-on-`src`-change and per-flag CLI
freshness are planned extensions.

## Corpus
`tests/test_docs_coverage_gate.py`: the real repo passes; synthetic temp trees
exercise the gap detectors.

## Try it
```bash
selfproof build --gates docs_coverage
```

## Evidence
Each run appends an evidence entry (`gate: docs_coverage`).
