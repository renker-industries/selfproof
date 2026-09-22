# What Selfproof proves, and what it does not

## In one sentence
Selfproof proves that named checks ran and passed at an exact commit — not that
the code is flawless.

## Why it matters
Overclaiming backfires on the first finding. A credible, bounded claim is the
stronger argument.

## How it works
Each gate returns `PASS`, `FAIL`, `SKIPPED(reason)` or `ERROR(reason)` and writes
a ledger entry bound to the commit SHA. A release requires zero findings of
medium or higher severity and zero `SKIPPED` among required gates.

## What it does not do
- It does not prove the absence of all bugs; no tool can.
- A green `proof` gate only covers what the configured commands test.
- The documentation gates measure presence, freshness and structure, not whether
  an explanation is good.
- A hash chain detects edited entries, not a truncated tail; the chain head is
  anchored in each release to make truncation detectable.

## Evidence
The strongest statement Selfproof makes has the form: "0 known findings at commit
`<sha>` per `<tools and versions>` on `<date>`."

## Try it
```bash
selfproof ledger verify
```
