# audit

**Primitive:** Audit

**Purpose:** Tamper-evident, queryable log of every security-relevant action. Cryptographically chained (hash chain over `sha256`) so that even a compromised agent cannot silently erase its own traces after the fact (see Vision, section 5.2). Tamper-**evident**, not immutable: modification is detectable, but an attacker who can rewrite both the log and its anchor is out of scope.

**Used by:** all three pillars.

Placeholder module without business logic.
