# 01 — Identity

## Concept
An **Actor** is any entity that can request an action: a human, an agent, a device, or a service.
Every actor has a canonical string identity called a **urn**: `kind:identifier`
(e.g. `agent:rencora-session-8f2c`).

## Why it exists
Authorization needs a stable, unambiguous answer to "who is asking?". A capability is granted *to a
specific actor*; if two actors could collide or an identifier could contain surprising characters,
the whole permission check becomes unreliable.

## Architecture
- `renker_core/identity/actor.py` — `Actor(kind, identifier)`, frozen dataclass.
- `.urn` builds `kind:identifier`; `Actor.from_urn` parses it back.
- `__post_init__` validates: kind ∈ {human, agent, device, service}; identifier non-empty, no
  whitespace, no `:`, `/`, or `\`.

## Security implications
The identifier is used inside capability matching and path-free contexts. Forbidding `:`/`/`/`\`
prevents an identifier from smuggling a second urn segment or a path fragment. This is *validation*,
not *authentication* — see `THREAT_MODEL.md §5` (forged identity is not closed here).

## Failure modes
- Passing a naive string urn instead of an `Actor` (bypasses validation) — always construct `Actor`.
- Assuming identity proves authenticity — it does not.

## Tests
`tests/test_identity.py` — urn roundtrip, rejected kinds, rejected identifiers (colon/whitespace/empty),
malformed urn parsing.

## Design trade-offs
Simplicity over cryptography: a plain validated string is enough for a single-host authorization slice,
and keeps the door open to add signed identities later without changing call sites.

---

## Questions (answer before reading the reference)

**Recall**
1. What are the four actor kinds?
2. What two parts make a urn, and what separates them?

**Code**
3. In which method is `agent:../etc` rejected, and which character triggers it?

**Debug**
4. A test builds `Actor("agent", "a b")` and expects success but gets `IdentityError`. Bug in the test
   or the code? Why?

**Security**
5. An attacker calls the guard with `Actor("human", "sebastian")` that they fabricated. Does identity
   validation stop them? What would?

**Architecture**
6. Why is `Actor` frozen (immutable)? What could go wrong if it were mutable and reused across checks?

--- reference ---
1. human, agent, device, service.
2. `kind` and `identifier`, separated by a single `:`.
3. `__post_init__`; the `:` (and also whitespace) check.
4. The test is wrong — whitespace is forbidden by design; `"a b"` is an invalid identifier.
5. No — validation only checks *shape*, not authenticity. Cryptographic authentication (signed actor
   tokens) would close it; today the caller must be trusted to supply the actor.
6. So an actor used in a policy decision can't be mutated between the check and the action (a TOCTOU-style
   risk), and so it can be safely hashed/compared and reused as a dict key.
