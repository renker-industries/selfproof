# THREAT_MODEL — renker-core (Phase 2 vertical slice)

**Scope of this document:** the first platform slice only — the guarded filesystem action
`Identity → Capability → Policy → Decision → Execute/Audit`. Claims here are limited to what
the code in `renker_core/{identity,capabilities,policy,audit,integration}` actually enforces,
verified by `tests/test_security_attacks.py`. Everything else is out of scope and is stated as such.

---

## 1. Assets — what we protect

- **A1 — Files outside a granted scope.** The agent must not read or write files it was not
  explicitly granted access to.
- **A2 — Integrity of the authorization decision.** A decision must follow deterministic rules;
  no input should turn a DENY into an ALLOW.
- **A3 — Integrity of the audit trail.** A recorded decision must be detectable if later altered.
- **A4 — Least privilege of grants.** A capability must not silently widen (e.g. a write grant
  must not also permit reads elsewhere).

We do **not** protect file *content confidentiality* (no encryption at rest here) and we do **not**
protect against a fully compromised host OS account.

## 2. Actors

| Actor | Trust | Notes |
|---|---|---|
| Human owner | trusted | issues/revokes capabilities |
| AI agent (rencora session) | **semi-trusted** | may be manipulated; its *intent* is untrusted |
| Local process | untrusted unless granted | must route through the guard to act |
| Remote service | untrusted | |
| Compromised agent | adversary | tries to exceed its capability |
| Malicious website / tool output | adversary | reaches the agent via prompt injection |

## 3. Trust boundaries

- **B1 — Agent reasoning ↔ enforcement.** The LLM/agent produces a *request*; the enforcement
  layer decides. The request is never trusted to be within bounds.
- **B2 — External content ↔ instructions.** Handled in rencora (`policy.wrap_external`); renker-core
  assumes the *request* may already be adversarial and still confines it to the capability.
- **B3 — Caller ↔ actor identity.** renker-core receives an `Actor`; it validates and canonicalizes it
  but does **not** cryptographically authenticate it (see §5, forged identity).

## 4. Attack surfaces and enforcement

| Surface | Enforced? | Mechanism |
|---|---|---|
| Path traversal (`drafts/../secret`) | ✅ | `Path.resolve()` then `is_relative_to(base)` — normalizes `..` before the check |
| Prefix confusion (`Documents2` vs `Documents`) | ✅ | comparison on resolved **path parts**, never string prefix |
| Capability escalation (read→write, wider path) | ✅ | exact `action == capability.capability`; scope check on resolved target |
| Confused deputy / wrong actor | ✅ | `capability.granted_to == actor.urn` required |
| Expired capability | ✅ | `expires_at` compared to UTC now |
| Revocation | ✅ | `CapabilityStore.revoke(id)`; policy denies revoked ids |
| Policy bypass via malformed input | ✅ | any missing/invalid capability or failed check → **DENY** (safe default) |
| Audit manipulation | ⚠️ partial | sha256 hash-chain + separate head anchor: detects modification, insertion, reordering, and tail truncation. Does **not** prevent deletion if the attacker can rewrite **both** log and anchor. |
| Replay | ⚠️ by design | a valid capability is reusable until expiry/revocation; no per-use nonce |
| Forged identity | ❌ not closed | renker-core validates format and matches `granted_to`, but does not authenticate the actor. The caller must supply a trusted `Actor`. |
| Prompt injection | out of core scope | mitigated in rencora; the core guarantee is that injection can change the *request* but **not** widen the *capability* |

## 5. Security properties — what this slice guarantees

1. **Confinement.** The guarded executor performs an action only if a matching capability —
   granted to the requesting actor, not expired, not revoked, permitting the exact action on a
   target inside its scope — exists. Otherwise it does not execute.
2. **Least privilege.** A capability permits exactly one action verb on one path scope. Nothing wider.
3. **Explainability.** Every decision returns a structured reason (actor, action, target, allowed scope).
4. **Auditability.** Every decision (allow and deny) appends one structured audit event.
5. **Tamper-evidence.** The audit chain + head anchor make modification/insertion/reordering/
   tail-truncation detectable by `AuditLog.verify()`.
6. **Safe default.** Errors, malformed input, and every unmet condition resolve to DENY. This extends to
   the enforcement config: if `config/renker_capabilities.json` exists but is unreadable/malformed while
   enforcement is intended, writes are denied (fail **closed**), never silently allowed.

## 5a. Robustness properties (added in the hardening pass)

- **Case correctness.** Scope containment compares `os.path.normcase`-normalized path parts, so on
  case-insensitive filesystems `~/Documents` and `~/documents` are the same scope, while `Documents2`
  is still rejected (prefix confusion stays closed). Verified by a 400-example property test that
  cross-checks `PathScope.permits` against `Path.is_relative_to` ground truth.
- **Input validation.** Empty/whitespace scope bases and actor identifiers with whitespace or control
  characters are rejected at construction. Empty/`None` targets and actions resolve to DENY without
  raising.
- **Concurrency.** `AuditLog.record` is guarded by a lock; 8 threads × 50 appends keep the hash chain
  valid and verifiable.
- **Durability.** Each entry is `fsync`ed and the head anchor is replaced atomically (`os.replace`).
- **Corruption reporting.** A corrupt JSON line surfaces as `AuditError`, not a raw parse error.

## 6. Explicit non-guarantees (do not market these as solved)

- No cryptographic **authentication** of actors (forged-identity is only mitigated by matching, not proven).
- No protection once the **host account is fully compromised** (attacker may delete log + anchor, or feed a forged trusted `Actor`).
- No **content confidentiality** (files are read/written in the clear).
- **No enforcement outside the guard.** An agent that calls the OS directly, bypassing
  `GuardedFilesystem`, is not constrained by renker-core. Enforcement is only as good as the
  routing of actions through the guard. Wiring rencora's dispatch to route through the guard is
  the next step and is tracked in `docs/archive/PHASE_2_REPORT.md`.
- **Audit crash window.** The append is `fsync`ed and the anchor replaced atomically, but they are two
  steps. A crash *between* them leaves the log with one more entry than the anchor records; `verify()`
  reports this as a head mismatch (indistinguishable at a glance from a one-entry truncation). This is a
  detected, operator-recoverable state — it is **not** silently ignored, and it is not tamper-proofing.
- **Multi-process audit.** The in-process lock does not coordinate multiple OS processes writing the same
  log file; a single writer (or an external file lock) is assumed.
- This is **not** an externally audited system.
