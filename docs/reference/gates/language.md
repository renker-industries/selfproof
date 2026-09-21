# Gate: language

## In one sentence
Flags files that appear to contain German text, enforcing the English-only rule.

## Why it exists
Serves W12 ("everything in English, not a single German file") and W17. It
replaces a promise with an executed check.

## What it checks
Every git-tracked text file (by suffix, from config) that is not excluded. A
line is flagged when it contains a German-specific letter (the a/o/u umlauts
and the sharp-s, upper or lower case) or at least three distinct common German
stopwords. Markers live in
`src/selfproof/gates/data/german_markers.json`.

## What blocks a change
Any flagged line in a non-excluded file yields `FAIL`.

## Tools and versions
Pure standard library (Python 3.11+). No external tool. Runs locally and in CI.

## Verdicts
- `PASS`: no scanned file looks German.
- `FAIL`: one or more non-excluded files contain German-looking lines.
- `ERROR`: `git ls-files` is unavailable or fails.
- `SKIPPED`: not used by this gate.

## Suppressions
Add the path prefix to `language.exclude` in `selfproof.toml` with a reason and
an expiry in the commit message. Excludes are visible in the gate result.

## Known false positives and false negatives
- False positive: proper names or quoted German inside English text.
- False negative: other non-English languages without these markers; German
  written without umlauts and with fewer than three stopwords on a line.
It is a floor, not a proof of good English.

## Corpus
- Known-bad: `tests/corpus/bad/language/` (umlaut and stopword cases).
- Known-good: `tests/corpus/good/language/`.
- Excluded fixture proving exclusion works: `tests/fixtures/non_english/`.

## Try it
```bash
selfproof build --gates language
```

## Evidence
Each run appends an evidence entry (`gate: language`) to the ledger.
`tests/test_language_gate.py` asserts the corpus contract.
