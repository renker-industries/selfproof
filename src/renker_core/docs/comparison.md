# Comparison with existing approaches

> **Note on sourcing.** Statements about *other* systems are general knowledge about those projects
> ("research"), not derived from this repository, and are current to the author's knowledge cutoff — verify
> before quoting externally. Statements about Renker are **repo-derived facts** (backed by code + tests).
> Renker is **not** claimed to be unique merely because its framing is; the point below is where it fits.

## The landscape

| Approach | Examples | What it solves | Where Renker differs |
|---|---|---|---|
| **Policy engines** | Open Policy Agent (Rego), AWS Cedar, OSO | Rich, general authorization decisions over structured input | Renker is narrower and deterministic-by-construction for agent file actions; the decision takes *only* trusted grants (no request-supplied attributes), which is a deliberate anti-prompt-injection stance. OPA/Cedar are far more expressive and battle-tested. |
| **Object-capability / token security** | ocap systems, macaroons, biscuit | Unforgeable, attenuable authority tokens | Renker's capabilities are simple immutable records in a store, not cryptographically attenuable bearer tokens. Macaroons/biscuit are stronger for distributed, offline delegation; Renker is simpler and local. |
| **OS sandboxing** | seccomp-bpf, AppArmor/SELinux, Windows AppContainer, Firejail | Constrain what a *process* can do at the kernel boundary | Renker constrains a *named actor's specific action* in-app, with expiry/revocation and an explainable, audited decision. OS sandboxes are a stronger, lower-level boundary; Renker is complementary and higher-level (and does not replace them). |
| **Audit / transparency logs** | Certificate Transparency, sigstore Rekor, hash-chained logs | Tamper-evident, sometimes externally-anchored append-only logs | Renker's audit is a local hash chain + head anchor: tamper-evident but not externally anchored or notarized. Rekor/CT are stronger (witnessed/gossiped); Renker is self-contained. |
| **Agent frameworks' guardrails** | in-prompt rules, tool allowlists in agent SDKs | Steer model behavior | Those live *inside* the model's decision loop; Renker's decision is *outside* it. Renker complements them. |

## Where Renker is stronger
- The security decision is **outside the LLM** and cannot read the request's claims — a clean structural
  answer to "the agent was convinced it was authorized." *(repo fact: test_trust_boundary.py)*
- Very small and dependency-free, so it is easy to read and audit end to end (~600 lines of core). *(repo fact)*
- Ships with adversarial + property + fuzz + concurrency tests and an honest threat model. *(repo fact)*

## Where Renker is weaker / unproven
- Far less expressive than OPA/Cedar; no attenuable tokens like macaroons; not a kernel boundary like seccomp;
  audit is not externally anchored like CT/Rekor.
- No cryptographic actor authentication; enforcement only for guarded file actions today; single-host, single
  writer; no third-party audit. *(repo facts / see claims.md)*

## Honest takeaway
Renker is not a replacement for policy engines, ocap tokens, OS sandboxes, or transparency logs. It is a
small, understandable, agent-shaped **composition** of capability + deterministic policy + tamper-evident
audit, whose distinctive stance is keeping the decision out of the model. For defense in depth, run it
*alongside* an OS sandbox, not instead of one.
