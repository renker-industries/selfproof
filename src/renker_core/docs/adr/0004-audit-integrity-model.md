# ADR 0004 — Audit integrity is a tamper-evident hash chain, not "immutable"

- **Status:** Accepted
- **Date:** 2026-08-10

## Context
A security audit trail must let you detect after-the-fact tampering, even by a compromised agent. But a
local file is not physically immutable, and claiming so would be dishonest.

## Decision
Each audit entry stores `prev_hash` and `entry_hash`, where
`entry_hash = sha256(canonical_json(payload) + prev_hash)` over a canonical (sorted-key, compact) JSON
serialization. A separate `.head` anchor file stores the latest `entry_hash` and is written atomically
(`os.replace`). `AuditLog.verify()` recomputes the chain from genesis and raises `AuditError` on modification,
insertion, reordering, tail truncation (via the anchor), or full deletion. Records are `fsync`ed and guarded
by an in-process lock. Reads/queries derive from the log file (source of truth); there is no separate mutable
index.

## Consequences
- We call this **tamper-evident**, never "immutable" (documentation forbids the stronger word).
- Detected-but-not-prevented cases are documented honestly: a crash between append and anchor is *detected*
  (not silently accepted); an attacker who rewrites **both** the log and the anchor, or the whole chain
  consistently, defeats it; multi-process writers need external locking. Closing these needs external
  anchoring/signing (deferred).
