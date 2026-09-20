# Working with Claude Code

The actual leverage lies not only in the product, but in the way it is built: trial-and-error becomes a systematic process.

## The basic loop

```
YOU (hypothesis)
   ↓
CLAUDE (implementation)
   ↓
AUTOMATED TESTS
   ├── PASS → done
   └── FAIL → CLAUDE ATTACKER → COUNTEREXAMPLE → CLAUDE FIX → (back to the tests)
```

## Extended loop for security-critical building blocks

For everything under `permissions/`, `capabilities/`, `crypto_interface/` (and the RenkerVault crypto layer), "Builder → done" never applies; instead:

```
Builder Agent → Attacker Agent → Reviewer Agent → Test Generator → Human Decision
```

## Concrete practice

1. **Every task gets a clear Definition of Done** before code is written — derived from the [[Roadmap]].
2. **Security-relevant changes** always go through the Builder→Attacker→Reviewer cycle.
3. **The attacker agent** is explicitly tasked to *break* the feature (e.g. "bypass a capability boundary with a manipulated website payload"). This is more than a code review.
4. **You remain the architect and final authority** — especially for policy decisions like "What counts as critical risk?". That is a product/value decision.
5. **`RENKER_VISION.md`** lives as a reference file in the repos, so that architecture questions are not reinvented in every session.

See also [`CONTRIBUTING.md`](../../CONTRIBUTING.md).
