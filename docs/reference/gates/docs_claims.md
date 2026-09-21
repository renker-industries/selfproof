# Gate: docs_claims

## In one sentence
Keeps user-facing claims honest: no absolute security claims, no unlabelled
numbers.

## Why it exists
Serves W8 (honesty is the most important rule) and R1. It enforces the promise
that every number or security statement is evidence-linked or labelled.

## What it checks
Over the user-facing docs (`README.md` and the `docs/wiki`, `docs/guides`,
`docs/explanation` trees): forbidden absolute claims (e.g. "unhackable",
"100% secure", "bug-free") unless the line negates them; and a bare percentage or
"percent" that lacks an evidence label (`planned`, `estimated`, `measured`,
`example`, `net`, `benchmark`, `sample size`) on the same line.

Internal records (`docs/CONCEPT.md`, `docs/decisions/`, `docs/reports/`) are not
scanned — they discuss numbers as labelled analysis, not product claims.

## What blocks a change
Any forbidden claim or unlabelled number yields `FAIL`.

## Tools and versions
Standard library only (`re`).

## Verdicts
- `PASS`: user-facing claims are labelled or negated.
- `FAIL`: at least one issue.
- `ERROR`/`SKIPPED`: not used.

## Suppressions
None by config; add a label or a negating disclaimer, or move the claim behind
generated evidence.

## Known false positives and false negatives
The negation check is line-local, so a disclaimer split across lines could be a
false positive. Executing `verify`-tagged code blocks in a sandbox is a planned
extension.

## Corpus
`tests/test_docs_claims_gate.py`: forbidden phrase flagged, negated disclaimer
allowed, unlabelled vs labelled percentage.

## Try it
```bash
selfproof build --gates docs_claims
```

## Evidence
Each run appends an evidence entry (`gate: docs_claims`).
