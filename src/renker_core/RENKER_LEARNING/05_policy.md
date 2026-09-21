# 05 — Policy Evaluation

## Concept
The **policy engine** takes an actor, an action, a target, and the capability store, and returns a
single explainable decision: `ALLOW`, `DENY`, or `REQUIRE_APPROVAL`.

## Why it exists
Enforcement must be one deterministic place, not scattered `if` checks. Every decision must carry a
human-readable reason, so a denial can be understood and a demo/audit is meaningful.

## Architecture
- `renker_core/policy/engine.py`
  - `evaluate(*, actor, action, target, store, now=None) -> PolicyResult`.
  - `PolicyResult(decision, reason, actor, action, target, allowed_scope, capability_id)`.
  - Rule order per candidate capability: wrong actor → wrong operation → expired → revoked →
    out of scope → approval policy (`deny`/`human`/`auto`).
  - No candidate at all → `DENY` ("no capability grants ...").

## Security implications
- **Safe default:** anything not explicitly allowed is denied.
- **Deterministic, not scored:** rules are readable and testable; no opaque risk score decides access.
- **Explainable:** the reason names actor, action, target, and allowed scope.

## Failure modes
- Forgetting that multiple capabilities can match — `evaluate` tries each and allows if any permits,
  otherwise returns the last denial reason. Overlapping grants should be intentional.
- Passing `now` inconsistently in tests (use timezone-aware datetimes).

## Tests
`tests/test_policy.py` — allow, deny-no-capability, require-approval, out-of-scope explainability.
Adversarial coverage in `tests/test_security_attacks.py`.

## Design trade-offs
Deterministic rules first (Phase 6 guidance). A scoring system was deliberately avoided: it would be
harder to audit and easier to bypass. Rules can be extended later without changing the ALLOW default
being "everything checked passed".

---

## Questions (answer before reading the reference)

**Recall**
1. What are the three possible decisions?
2. What is returned when no capability matches at all?

**Code**
3. In `_evaluate_one`, which check comes first: expiry or wrong-actor? Why does order matter for the
   reason shown?

**Debug**
4. A request you expect to ALLOW returns `REQUIRE_APPROVAL`. Which capability field explains it?

**Security**
5. Why is "default DENY" safer than "default ALLOW with a blocklist"?

**Architecture**
6. Why return a `PolicyResult` with a `reason` instead of just a boolean?

--- reference ---
1. `ALLOW`, `DENY`, `REQUIRE_APPROVAL`.
2. `DENY` with reason "no capability grants <action> to <actor>".
3. Wrong-actor is checked before expiry. Order matters because the *first* failing check produces the
   reason; you want the most fundamental mismatch (not your grant at all) reported first.
4. `approval_policy == "human"`.
5. A blocklist fails open: anything you forgot to list is allowed. Default DENY fails closed: only
   explicitly permitted actions pass, so omissions are safe.
6. Because denials must be explainable (for the user, the demo, and the audit trail); a boolean throws
   away the *why*.
