# 11 — The Trust Boundary (decision outside the LLM)

## Concept
The security decision must not depend on anything the agent (or a manipulated tool/webpage) can control.
Prompt injection may change *what the agent requests*; it must never change *what the system allows*.

## Why it exists
An LLM can be talked into anything. If authorization logic reads the model's output ("I am authorized",
`riskTier=low`, a tool result claiming permission), then injection becomes privilege escalation. Moving the
decision outside the model closes that path structurally.

## Architecture
- `renker_core.policy.evaluate(*, actor, action, target, store, now=None)` — the decision uses **only**
  trusted inputs: the actor, the requested action/target, and the grants in the store. There is deliberately
  **no** `context`, `risk`, `approval_policy`, or `authorized` parameter.
- Risk tier and approval policy live on the **immutable** `Capability` in the store (granted by a human/config),
  never on the request.
- Unknown actions and any failed check → DENY (fail closed).

## Security implications
Injection can only influence `(action, target)` — and those are exactly what the policy checks against the
grant. It cannot inject an authorization or lower its own risk. Confused-deputy is prevented because authority
is bound to `actor + capability + scope + action` and never transfers implicitly.

## Failure modes
- Re-introducing a `context`/metadata parameter that the request can populate would reopen the hole.
- Reading risk/approval from the request instead of the capability.
- Enforcing only some actions (an unguarded path bypasses the boundary entirely).

## Tests
`tests/test_trust_boundary.py`: injected credential/scope requests → DENY; tool-output "authorization" has no
effect; other actor / other target denied; `evaluate` signature has no request-authorization parameter;
capability is immutable; `human` approval forces REQUIRE_APPROVAL; unknown action fails closed.

## Design trade-offs
Determinism over expressiveness: a richer policy language (attributes, request context) would be more
flexible but would put attacker-influenced data back into the decision. For agent security that trade is not
worth it here.

---

## Questions (answer before the reference)

**Recall**
1. What are the only inputs to `evaluate`?
2. Where does a capability's risk tier come from — the request or the grant?

**Code**
3. Which test proves the request cannot supply its own authorization, and how does it prove it *structurally*?

**Debug**
4. A teammate adds `context: dict` to `evaluate` and reads `context["authorized"]`. Why is that a security
   regression, and which test should fail?

**Security**
5. Explain, in one sentence, why prompt injection cannot escalate privilege here.

**Architecture**
6. If you had to support "this action is fine in a break-glass emergency", how would you add it *without*
   letting the agent trigger break-glass itself?

--- reference ---
1. `actor`, `action`, `target`, `store` (and an optional `now` for tests).
2. The grant (the immutable capability in the store), set by a human/config.
3. `TestRiskIsNotRequestControlled::test_evaluate_has_no_request_authorization_input` — it inspects the
   function signature and asserts no `context`/`risk`/`authorized`/etc. parameter exists.
4. It puts attacker-influenceable data into the decision; `test_evaluate_has_no_request_authorization_input`
   should fail.
5. Because the decision reads only trusted grants + the requested action/target, so a convinced agent can
   still only request — the grant, not the request, decides.
6. Model break-glass as its own capability/approval_policy granted out-of-band (human/config), audited, and
   time-bound — never a flag the agent can set.
