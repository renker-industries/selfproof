# ADR 0001 — Tech stack for renker-core

- **Status:** Accepted
- **Date:** 2026-08-10
- **Decider:** Sebastian Renker (architect, final authority)

## Context

`renker-core` is the shared foundation for the three product pillars of the Renker platform. It must be consumable by all three without containing their business logic. The language choice should minimize friction for the *primary* consumers of the first primitives (Identity, Permissions, Audit — Vision, section 14).

Current state of the three existing product repos (verified on 2026-08-10, details in [`../status/repo-audit.md`](../status/repo-audit.md)):

| Repo | Language/stack |
|---|---|
| **rencora** (ACT) | Python (`requirements.txt`, `main.py`, PyInstaller via `main.spec`) |
| **continuum** (LEARN) | Python (`pyproject.toml`, `src/`) |
| **renkervault** (SECURE) | TypeScript/React + Tauri (Rust) client, Node.js relay server |

The stack is therefore **not** fully uniform: two of three repos are Python, one is TypeScript/Rust.

## Decision

**renker-core is implemented in Python (>=3.10).**

Rationale:

1. **Primary consumers are Python.** The first concretely needed primitives (Identity, Permissions, Audit) serve Rencora first — and Rencora is Python. Continuum, the second major consumer of Memory/Evidence/Experiments, is also Python.
2. **Majority + character of the code.** Two of the three repos are Python, and they are exactly the agent- and reasoning-heavy ones (ACT, LEARN). The Vision heuristic is: "Python when ML/agent-reasoning building blocks dominate" — which applies here.
3. **Interoperability instead of a single language.** renker-core also defines a cross-product `protocol/` wire format. The actual cross-product compatibility runs via this format, not via a shared implementation language. RenkerVault (TS/Rust) therefore consumes the primitives via the protocol/schema, not through a direct Python import.

## Alternatives considered

- **TypeScript/Node.js.** Advantage: RenkerVault is already TS, and the Vision heuristic names TS for "cross-platform CLI/browser/OS automation". Disadvantage: the two primary consumers to be served first (rencora, continuum) are Python; a TS core would introduce a language boundary for them at every call. **Rejected**, because it increases friction at the immediate milestones.
- **Rust.** Advantage: proximity to the Tauri part of RenkerVault, strong safety guarantees for a security-critical foundation. Disadvantage: the highest entry and iteration cost in a phase where fast, test-driven iteration matters; none of the Python consumers benefit directly. **Deferred** — remains an option for a later, tightly scoped `renker-crypto` module.

## Consequences

- **Positive:** rencora and continuum can import renker-core directly; fast iteration; uniform test/lint tooling (`pytest`, `ruff`).
- **Negative / to note:** RenkerVault cannot import renker-core directly. The cross-product boundary runs via `protocol/` (wire format/schema). As soon as RenkerVault needs primitives directly, either a language-neutral schema (e.g. JSON Schema / Protobuf) or a thin language port must be maintained.
- **Crypto stays out.** `crypto_interface/` contains interfaces only; the implementation deliberately stays outside this repo (Vision, section 4.3), which makes renker-core's language choice irrelevant to crypto security.
