# Agent Security

Potentially the economically strongest short-term building block of the platform.

## The core problem

AI agents are getting more and more permissions. What happens when an agent is manipulated?

```
Website → Prompt Injection → AI Agent → Tool Call → "Upload ~/.ssh/"
```

## The answer: capability security

No actor holds blanket rights. Every capability is an individually granted, individually revocable object with six properties: **Permission, Scope, Lifetime, Audit Trail, Approval Policy, Revocation.**

The flow of every action:

```
REQUEST → POLICY ENGINE → Risk Assessment → Permission → Sandbox → Execution → Audit
```

For dangerous actions: `HIGH RISK → DENY` or `→ HUMAN APPROVAL`.

## Permission object (sketch)

```json
{
  "capability": "filesystem.write",
  "scope": "~/Documents/drafts/**",
  "grantedBy": "user:sebastian",
  "grantedTo": "agent:rencora-session-8f2c",
  "issuedAt": "2026-08-09T10:00:00Z",
  "expiresAt": "2026-08-09T11:00:00Z",
  "approvalPolicy": "auto",
  "riskTier": "low",
  "revocable": true,
  "auditRequired": true
}
```

## Audit-log entry (sketch)

```json
{
  "eventId": "evt_9a31...",
  "timestamp": "2026-08-09T10:14:02Z",
  "actor": "agent:rencora-session-8f2c",
  "action": "filesystem.write",
  "target": "~/Documents/drafts/report.md",
  "capabilityRef": "cap_5521...",
  "riskAssessment": "low",
  "decision": "allowed",
  "outcome": "success",
  "chainHash": "sha256:..."
}
```

The log is **append-only** and cryptographically chained (hash chain), so that even a compromised agent cannot erase its traces (tamper-evident).

## Risk levels (basis of the policy engine)

| Level | Examples | Default |
|---|---|---|
| **Low** | Reading in scope, web research in an allowlist | auto allowed, logged |
| **Medium** | Writing outside known scopes, a new domain | allowed with a warning / approval per policy |
| **High** | Credentials/keys, deletion, payments | human approval |
| **Critical** | `.ssh`, production DB, irreversible deletion | denied, only with an explicit override |

This can become a standalone product: **Renker Agent Security** — *security layer for autonomous AI agents*. The business case is the **damage avoided**, immediately measurable in euros.
