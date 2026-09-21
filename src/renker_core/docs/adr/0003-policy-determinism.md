# ADR 0003 — Deterministic, explainable policy; the security decision is outside the LLM

- **Status:** Accepted
- **Date:** 2026-08-10

## Context
Autonomous agents are driven by an LLM whose output can be manipulated (prompt injection). If the security
decision depended on LLM reasoning or on request-supplied metadata, an attacker could talk the system into
allowing an action.

## Decision
`evaluate()` is a pure, deterministic function of exactly four trusted inputs: `actor`, `action`, `target`,
and the `CapabilityStore` (plus an optional `now` for testability). It returns `ALLOW` / `DENY` /
`REQUIRE_APPROVAL` with a human-readable reason. It has **no** `context`, `risk`, `authorized`, or
`approval_policy` parameter — the request cannot supply its own authorization or risk. Risk tier and
approval policy come only from the immutable capability in the store (granted by a human/config).
Unknown actions and any unmet condition **fail closed** (DENY).

## Consequences
- The security boundary is structurally outside the LLM: prompt injection can change *what is requested*,
  never *what is allowed* (tested in `test_trust_boundary.py`).
- Decisions are reproducible and explainable (no opaque scoring), which suits audit and demos.
- Adding rule types later must preserve determinism and the "ALLOW only if every check passed" default.
