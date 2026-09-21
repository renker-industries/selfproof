# Architecture

## Big picture

The Renker platform deliberately separates **primitives** (shared) from **business logic** (product-specific). Rencora knows nothing of Continuum experiments and vice versa — but both speak the same vocabulary for "Who am I", "What may I do", "What happened", and "What is substantiated".

This avoids two traps:

- **Monolith trap:** cram everything into one app → loss of focus, blocking releases.
- **Silo trap:** three separate codebases reinventing security/identity three times (triple the error-proneness).

## The three pillars

- **Rencora (ACT):** "A personal AI agent that can actually operate your computer — while being controlled by explicit security boundaries." The core is the *controllable agent runtime*, independent of the thinking LLM.
- **RenkerVault (SECURE):** not a Signal replacement, but a secure communication and identity layer for agents and humans. It also secures agent-to-agent and agent-to-human communication. Principle: *the server gets as little trust as possible* (relays ideally transport ciphertext only).
- **Continuum (LEARN):** deliberately positioned modestly as an *autonomous research & discovery engine*, not as "AGI".

## renker-core — the foundation

A fourth repository, so that the three products do **not** build their own, incompatible versions of identity, authorization, and history. The nine primitives:

| Primitive | Purpose |
|---|---|
| **Identity** | Verifiable identity for human, agent, device, service |
| **Permissions** | Capability model, generically usable |
| **Memory** | Episodic + semantic memory with source references |
| **Events** | Append-only event log as the backbone for audit/reactivity |
| **Tasks** | Uniform representation of "things to be done" |
| **Experiments** | Hypothesis → design → execution → result |
| **Evidence** | Evidence-status model, also for Rencora actions |
| **Security** | Threat model, sandbox boundaries, crypto interfaces |
| **Audit** | Tamper-evident, queryable log |

(Plus `protocol/` as the wire format between products/devices.)

## The crypto boundary

A deliberate design decision: the cryptography **implementation** does *not* move into Core. `crypto_interface/` contains interfaces only. The real implementation stays in its own minimal, strictly audited module based on established primitives (libsodium/NaCl, Signal protocol) — never as an in-house design. This keeps the attack surface small and external audits realistic (see [[Agent-Security]]).

## Tech stack

renker-core is implemented in **Python** — rationale and alternatives in [`docs/adr/0001-tech-stack.md`](../adr/0001-tech-stack.md). In short: the two primary first consumers (Rencora, Continuum) are Python; RenkerVault (TS/Tauri) consumes via the `protocol/` wire format.
