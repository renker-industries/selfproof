# Gate: proof

## In one sentence
Runs the configured test, lint and type commands and binds the result to the
exact commit.

## Why it exists
Serves W2, W3 and the first promise: every "done"/"correct" statement is backed
by an executed check bound to the commit (concept sections 1, 5).

## What it checks
Each command in `proof.commands` (default: `python -m pytest -q` and
`python -m ruff check .`). The current commit SHA is recorded so a result for a
different SHA (a stale proof) is detectable.

## What blocks a change
Any command exiting non-zero yields `FAIL`. If no command failed but one was
skipped (missing tool), the gate returns `SKIPPED`, which is not a pass and is
not release-ready.

## Tools and versions
Orchestrates the project's own dev tools: `pytest` (>=8), `ruff` (>=0.6). It
does not reimplement them. Configure exact commands in `selfproof.toml`.

## Verdicts
- `PASS`: every configured command exited 0.
- `FAIL`: at least one command exited non-zero.
- `SKIPPED`: no failure, but at least one tool was missing or timed out.
- `ERROR`: reserved for unexpected runner failures.

## Suppressions
None. A proof cannot be suppressed; fix the failing command or change the
configured command set through a reviewed PR.

## Known false positives and false negatives
A green proof only covers what the configured commands actually test. Coverage
and mutation strength are separate metrics (M8).

## Corpus
Exercised by `tests/test_proof_gate.py`: pass, fail, missing-tool-is-skipped,
and fail-wins-over-skip.

## Try it
```bash
selfproof build --gates proof
```

## Evidence
Each run appends an evidence entry (`gate: proof`) with the bound commit SHA.
