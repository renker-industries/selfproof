# Selfproof

> Provider-neutral platform that checks AI-written code for slop and security
> problems, records evidence for every check, and builds itself through a
> controlled loop of agents and its own gates. Its kernel is `renker-core`.

**Status: bootstrapping (private).** This repository is being built by an
autonomous local agent under a written authorization charter
([`AUTONOMY_CHARTER.md`](AUTONOMY_CHARTER.md)). Nothing here is released. Many
components described in the [concept](docs/CONCEPT.md) are `planned`, not built.

## What Selfproof promises (and nothing beyond it)

1. Every "done", "correct" or "secure" statement is backed by an executed check
   bound to the exact commit.
2. Every check leaves an entry in a tamper-evident ledger anyone can verify.
3. Each release has zero known open findings of severity medium or higher,
   according to named tools, versions and date.
4. Everything it claims about itself is evidence-linked or labelled `planned`.

It does **not** promise "absolutely secure", "unhackable" or "no bugs". See
[SECURITY.md](SECURITY.md).

## Honest self-building

An AI agent (by default Claude Code, run locally by the maintainer) writes each
change on a branch. Selfproof's own gates check the change and record evidence.
Changes to the gates, the kernel and other protected paths always require a
human. The language model writes the code, the gates check it, and a human owns
the rules.

## Quickstart (once built)

```bash
selfproof status          # current phase and metrics
selfproof ledger verify   # recompute the evidence chain
selfproof build           # run one build-loop task
```

## Layout

See [docs/CONCEPT.md](docs/CONCEPT.md) section 4.4 and the per-directory READMEs
under `src/`.

## License

New code is Apache-2.0 ([LICENSE](LICENSE), [NOTICE](NOTICE)). The imported
kernel `src/renker_core/` is proprietary until relicensing (charter A3) is
executed; its own `LICENSE` governs that subtree until then.
