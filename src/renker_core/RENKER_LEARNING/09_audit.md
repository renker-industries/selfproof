# 09 — Audit Trails

## Concept
An **audit trail** is a record of every security-relevant decision. Renker's is **tamper-evident**:
altering a past entry can be *detected*, even if not *prevented*.

## Why it exists
"Trust but verify." If a decision is later disputed — or an agent is compromised — you need a record
whose modification you can detect. Note the honest word: *evident*, not *immutable*.

## Architecture
- `renker_core/audit/log.py`
  - `AuditLog.record(...)` appends one JSON line and updates a `.head` anchor file.
  - Each entry stores `prev_hash` and `entry_hash`; `entry_hash = sha256(canonical(payload) + prev_hash)`.
  - `verify()` recomputes the chain from genesis; it raises on: modified entry (hash mismatch),
    reordering/insertion (prev_hash mismatch), tail truncation (last hash ≠ head anchor), and full
    deletion (empty log but non-genesis anchor).

## Security implications
The hash chain links each entry to the previous one, so any single change breaks the chain downstream.
The separate `.head` anchor extends detection to tail truncation. **Limitation:** an attacker who can
rewrite *both* the log and the anchor can still erase history — this is documented, not hidden
(`THREAT_MODEL.md §6`). Do **not** call this "immutable".

## Failure modes
- Deleting the `.head` anchor (verify treats a present-but-mismatched anchor as tampering; a missing
  anchor with entries would fail the tail check).
- Assuming append-only-on-disk equals integrity — it does not without the chain.

## Tests
`tests/test_audit.py` — chain links + verify, modified entry, tail truncation, full deletion, roundtrip.

## Design trade-offs
A file + hash chain is simple, dependency-free, and demonstrable. It is *not* a distributed or
notarized ledger; that would be over-engineering for a single-host first slice.

---

## Questions (answer before reading the reference)

**Recall**
1. What two hashes does each entry carry?
2. What is the `.head` anchor for?

**Code**
3. What goes into the sha256 that produces `entry_hash`?

**Debug**
4. `verify()` raises "head anchor mismatch". What most likely happened to the log?

**Security**
5. Why is it wrong to call this log "immutable"? What word is correct, and what attack still defeats it?

**Architecture**
6. Why chain each entry to the previous hash instead of just hashing entries independently?

--- reference ---
1. `prev_hash` (link to the previous entry) and `entry_hash` (this entry's hash).
2. To detect tail truncation — it stores the latest `entry_hash` separately, so dropping trailing
   entries is detectable.
3. The canonical JSON of the entry payload concatenated with the previous entry's hash.
4. Trailing entries were removed (or the file was replaced with an earlier version).
5. Nothing prevents modification; it only makes modification *detectable* — so it is "tamper-evident".
   An attacker who rewrites both the log and the `.head` anchor still defeats it.
6. Independent hashes let an attacker delete/reorder whole entries undetected; chaining ties them into a
   sequence so any removal or reordering breaks the following links.
