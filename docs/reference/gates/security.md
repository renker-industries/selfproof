# Gate: security

## In one sentence
Scans for secrets, license problems and workflow-hardening gaps, augmented by
external scanners when installed.

## Why it exists
Serves W5 and the threat model (leaked secrets, compromised CI, forbidden
licenses).

## What it checks
Built-in (always run): a regex secret scan of tracked text files (the match
value is never printed); a license check (LICENSE present, no forbidden
dependency license); a workflow check (each `.github/workflows/*.yml` declares
`permissions:` and avoids `pull_request_target`). External augmenters when on
PATH: `gitleaks`, `osv-scanner`, `zizmor`.

## What blocks a change
Any built-in finding yields `FAIL`.

## Tools and versions
Standard library for the built-ins. External tools are pinned and recorded in a
scouting ADR when adopted; today they augment only if already installed.

## Verdicts
- `PASS`: no findings. The built-in checks always run and cover the baseline;
  the output names which external scanners ran and which are not installed.
- `FAIL`: at least one finding, from a built-in check or from an external
  scanner (gitleaks/zizmor) that actually ran.
- `ERROR`: reserved.

An absent external scanner is reported as "not run", not as a pass: the gate
never treats a missing tool as extra confidence, and CI installs the scanners so
they run there. `osv-scanner` advisory scanning is vacuous with zero runtime
dependencies.

## Suppressions
None by config. A real secret must be rotated at the provider (manual) and the
file cleaned; the location is recorded, never the value.

## Known false positives and false negatives
The built-in secret regexes catch common shapes, not all secrets; the generic
assignment rule can miss obfuscated values. External scanners close much of this
gap and are required for a release (Phase 8).

## Corpus
- Known-bad: `tests/corpus/bad/security/` (AWS example key, private-key header,
  password assignment).
- Known-good: `tests/corpus/good/security/`.

## Try it
```bash
selfproof build --gates security
```

## Evidence
Each run appends an evidence entry (`gate: security`).
