# Positioning — Renker (agent security slice)

## One line
Renker keeps the security decision **outside** the AI. An autonomous agent may *request* an action, but a
deterministic capability-and-policy layer decides whether it runs — and records every decision in a
tamper-evident audit trail.

## The problem
AI agents are getting file, shell, and network access. A manipulated agent (prompt injection, a malicious
web page, a poisoned tool result) can be talked into exfiltrating credentials or deleting data. Guardrails
built *inside* the model can themselves be talked around.

## The approach
- **Capabilities, not blanket access.** "May write to `~/Documents/drafts/**`", not "has filesystem access".
- **The decision is deterministic and outside the LLM.** `evaluate(actor, action, target, grants)` — the
  request cannot supply its own authorization or risk.
- **Every decision is audited.** A sha256 hash chain with a head anchor makes tampering detectable.
- **Fails closed.** Unknown actions, malformed input, and misconfiguration deny by default.

## Who it's for
Teams giving agents real capability in environments where a mistake is expensive — regulated and
records-sensitive settings (healthcare, legal, finance) are the sharpest fit. The value is the *prevented*
incident, measurable in avoided cost.

## What it is today (honest)
A small, tested Python foundation (`renker-core`, ~600 lines, zero runtime dependencies) plus an opt-in guard
wired into one real agent's (rencora) file writes. It is a strong, demonstrable **vertical slice**, not an
externally audited product. See `claims.md` for the exact verified/unverified/future split.

## The strongest asset
The working demo: allow a permitted read, deny an out-of-scope read, show the verifiable audit trail —
reproducible from a clean checkout in one command.
