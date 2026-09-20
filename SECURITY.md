# Security model — renker-core

`renker-core` provides the primitives with which the Renker platform makes autonomous action **controllable, auditable, and revocable**. This document summarizes the capability and risk-level model (full version: `RENKER_VISION.md`, section 5).

## Capability security

No actor holds blanket rights ("terminal access", "filesystem access"). Every capability is an individually granted, individually revocable object with six properties:

- **Permission** — exactly which action is allowed (not "filesystem", but "read, under this path prefix").
- **Scope** — the concrete boundary (path, domain, process name).
- **Lifetime** — expiry time or session binding; no capability lives forever by default.
- **Audit Trail** — every use is logged tamper-evidently.
- **Approval Policy** — `auto` / `deny` / `human`, depending on risk.
- **Revocation** — instantly revocable at any time, even in the middle of a running action.

## Risk levels

| Level | Example actions | Default behavior |
|---|---|---|
| **Low** | Read a file in an allowed scope, web research in an allowlist | automatically allowed, logged |
| **Medium** | Write a file outside known scopes, contact a new domain | allowed with a warning or approval per policy |
| **High** | Access to credentials/keys, delete operations, payment triggering | human approval required |
| **Critical** | Access to `.ssh`, production databases, irreversible deletion | denied by default, only with an explicit override |

## Audit log

Security-relevant actions are logged append-only and cryptographically chained (hash chain over `sha256`), so that even a compromised agent cannot silently erase its traces after the fact. This makes tampering **detectable** (tamper-evident), not impossible (an attacker who can rewrite both the log and its anchor is out of scope).

## Cryptography

`renker_core/crypto_interface/` contains **interfaces only**. No cryptography of its own is implemented; the implementation lives in a separate, strictly audited module based on established primitives (libsodium/NaCl, Signal protocol). See Vision, section 4.3.

## Reporting vulnerabilities

Please do **not** report security issues via public issues, but confidentially to the repository owner. Since this repo is private, a direct contact suffices for now.
