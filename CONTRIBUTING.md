# Contributing

Selfproof is built through its own loop, but the same rules apply to any change.

## Language
English only, everywhere (code, comments, commits, docs). The `language` gate
enforces this. The single exception is `tests/fixtures/non_english/`.

## Commits
Use [Conventional Commits](https://www.conventionalcommits.org/) and end every
commit with a `Built-by` trailer:

```
feat: add the slop gate

Built-by: agent claude-code opus-4-8
```

`Built-by: human` for hand-written commits, `Built-by: agent <name> <version>`
for agent-written ones. The self-built share is computed from these trailers, so
they must be honest.

## Every change goes through a branch and a PR
After the first commit, never push to `main`. Keep PRs small, one concern each,
and fill in the PR template — including the documentation checklist.

## Gates must pass
Run the gates locally before opening a PR:

```bash
PYTHONPATH=src:src/renker_core python -m selfproof.cli build
PYTHONPATH=src:src/renker_core python -m selfproof.cli ledger verify
```

A missing tool is `SKIPPED`, never a pass. Releases need zero `SKIPPED` among
required gates.

## Protected paths need approval
Changes under the protected paths (see `CODEOWNERS` and concept 2.3) are Tier B:
they are built and proven, but merge only after a signed human approval.

## Never (Tier C)
Weakening or deleting a gate, test or threshold to make something pass;
disabling branch protection; editing the ledger, the charter or the ratchet
baseline by hand. The kernel refuses these.
