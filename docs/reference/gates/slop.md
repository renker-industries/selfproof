# Gate: slop

## In one sentence
Catches typical AI-generated slop in shipped Python code.

## Why it exists
Serves W3 (slop-free code) and the threat model's "invented code" concern.

## What it checks
Dependency-free AST + text heuristics over `selfproof` source and tests (kernel
excluded): `...` placeholder bodies (outside `@overload`/`@abstractmethod`),
placeholder markers (`TODO`, `FIXME`, `XXX`, `HACK`) in comments, broad
`except`/`except Exception` whose body is only `pass`, and `test_*` functions
with no assertion.

## What blocks a change
Any finding yields `FAIL`.

## Tools and versions
Standard library only (Python 3.11+). Runs locally and in CI.

## Verdicts
- `PASS`: no slop found.
- `FAIL`: one or more findings.
- `ERROR`: cannot list Python files.
- `SKIPPED`: not used by this gate.

## Suppressions
Add the path prefix to `slop.exclude` in `selfproof.toml` with a reason and
expiry in the commit message.

## Known false positives and false negatives
`raise NotImplementedError` is intentionally allowed (legitimate abstract
method). Dead-code and copy-paste detection are **not** implemented here; they
are deferred to external tools (vulture, jscpd) under a future ADR.

## Corpus
- Known-bad: `tests/corpus/bad/slop/`.
- Known-good: `tests/corpus/good/slop/`.

## Try it
```bash
selfproof build --gates slop
```

## Evidence
Each run appends an evidence entry (`gate: slop`). `tests/test_slop_gate.py`
asserts the corpus contract.
