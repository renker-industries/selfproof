# Gate: test_weakening

## In one sentence
Blocks changes that quietly weaken the checks by deleting tests/assertions or
adding skip markers.

## Why it exists
Serves the threat "gates that are too strict get worked around" and the Tier C
prohibition on weakening a test to pass (concept 2.3, 2.5).

## What it checks
Diff-based, compared against the merge-base with `main`: removed `assert` lines,
removed `def test_...` definitions, and added skip/xfail markers
(`@pytest.mark.skip`, `pytest.skip(`, `@pytest.mark.xfail`, `unittest.skip`).

## What blocks a change
Any such change yields `FAIL`. A finding makes the change Tier B: it needs a
signed human approval. The gate never merges anything itself.

## Tools and versions
`git` plus the standard library. Runs locally and in CI (CI checks out full
history so the merge-base resolves).

## Verdicts
- `PASS`: no weakening found, or no comparison base exists (fresh repo / `main`
  unresolved / running on `main` itself).
- `FAIL`: at least one weakening change in the diff.
- `ERROR`/`SKIPPED`: not used; an unavailable base is treated as `PASS` with a
  note, because there is genuinely nothing to compare.

## Suppressions
None by config. A legitimate test removal is a Tier B change approved by the
owner, not a suppression.

## Known false positives and false negatives
"Loosened thresholds" cannot be detected generically and are left to review.
Renaming a test counts as a removal plus an addition; the reviewer judges intent.

## Corpus
Integration tests in `tests/test_test_weakening_gate.py` build a temporary git
repo for each case (removed assertion, added skip, no-base pass).

## Try it
```bash
selfproof build --gates test_weakening
```

## Evidence
Each run appends an evidence entry (`gate: test_weakening`).
