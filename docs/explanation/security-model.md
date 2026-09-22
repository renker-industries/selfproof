# Security model

## In one sentence
Enforcement lives outside the agent — in git, CI and a deterministic kernel —
and protected changes need a signed human approval.

## Why it matters
Not every agent has hooks, and a model can be talked into anything by injected
text. Controls that do not depend on the model are the only reliable ones.

## How it works
- **The kernel decides.** Every agent action and every merge is submitted to
  `renker-core`, which returns `ALLOW`, `DENY` or `REQUIRE_APPROVAL`, fail-closed.
- **Protected paths.** The gates, the kernel, the rules, CI, the license and the
  charter need a signed approval to change.
- **Untrusted input.** Issue and web text is data, never instructions; the
  self-build loop runs only on maintainer-labelled issues, locally, without
  secrets.
- **Supply chain.** A new dependency needs a registry check and an ADR line; the
  kernel keeps zero dependencies.

## What it does not do
- It does not yet cryptographically authenticate actors; until signed identities
  exist, the git commit signature carries that trust.
- On the current plan, server-side branch protection and secret scanning are
  unavailable for a private repository; enforcement relies on the hooks and CI
  until publication or a plan upgrade. This is recorded in the owner to-do list.

## Evidence
See [`docs/threat-model.md`](../threat-model.md) once populated, `SECURITY.md`,
and the `security` gate reference.

## Try it
```bash
selfproof build --gates security
```
