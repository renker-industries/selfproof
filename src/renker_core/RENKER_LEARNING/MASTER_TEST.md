# Master Test — design a protected action without looking

This is the real learning metric. Do it **without opening the implementation first**. Give yourself ~45
minutes. Then compare with the code.

## The challenge
Design (and, if you can, implement) a protected `filesystem.append` action for the Renker slice. You are
given only these building blocks — nothing else:

```
Identity     : a validated actor (kind:identifier)
Capability   : actor-bound, scoped, time-bound, revocable, immutable
Policy       : deterministic decision ALLOW / DENY / REQUIRE_APPROVAL, explainable
Audit        : tamper-evident, every decision recorded
Action       : append text to a file
```

## Design it on paper first
Answer before writing any code:

1. **Flow.** Draw the path from "agent requests append" to "audit event". Name each step.
2. **Inputs to the decision.** Exactly which values may the policy read? Which must it *ignore*, and why?
3. **The capability.** What are its fields for an append grant? What is its scope, and how do you stop
   `drafts/../secret.txt`?
4. **Failure modes.** List five ways this could go wrong (expired grant, wrong actor, out of scope, revoked,
   unknown action) and the expected decision for each.
5. **Audit.** What fields does the append decision record? How would someone later detect that you deleted the
   deny events?
6. **The attack.** Write one prompt-injection scenario and explain why it cannot widen the append authority.

## Then implement (optional but recommended)
- Add `APPEND = "filesystem.append"` to the guard and an `append(actor, target, content)` method that runs the
  same pipeline and appends on ALLOW.
- Write at least: one allow test, one out-of-scope deny, one wrong-actor deny, one expired deny, and one audit
  assertion.

## Compare
Now read `renker_core/integration/filesystem.py`, `renker_core/policy/engine.py`, and
`tests/test_integration.py`. For each difference, ask: *is mine weaker, equal, or stronger — and why?*

## You pass if you can answer
- Why does the decision ignore the request's claims?
- What happens if `renker_core` (or the guard) is bypassed entirely?
- How would an attacker try to defeat the audit, and what stops the easy versions?
- How would you redesign scope checking if `resolve()` were unavailable?

Write your answers down. If you can explain all four without the code open, you own this subsystem.
