# How self-building works

## In one sentence
An AI agent writes each change on a branch, Selfproof's own gates check it and
record evidence, and a human owns the rules.

## Why it matters
A system that can rewrite its own checks and approve itself is exactly the
failure mode Selfproof exists to prevent. So autonomy is bounded: the agent
never changes the rules on its own.

## How it works
1. A task becomes a branch in an isolated worktree.
2. The agent writes the change.
3. The local gates run; up to three repair attempts are allowed.
4. A pull request carries the evidence. CI re-runs the gates.
5. Tier A changes (docs, tests, non-protected code) merge when every proof
   passes. Tier B changes (protected paths: the gates, the kernel, the rules,
   CI, the charter) wait for a signed human approval.
6. Tier C actions — weakening a gate, editing the ledger, forging an approval —
   are refused by the kernel.

## What it does not do
It does not run unsupervised. It does not merge a change to a protected path
without a human. It does not force a green result: a task that keeps failing is
recorded as a failure.

## Evidence
Every commit carries a `Built-by: human` or `Built-by: agent <name>` trailer,
and the dashboard shows the self-built share with failures included. The cutover
to self-hosting is anchored by the `self-host-v0` tag.

## Try it
```bash
selfproof build
selfproof dashboard show
```
