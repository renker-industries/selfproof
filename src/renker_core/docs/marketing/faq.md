# FAQ

**Is this a firewall / antivirus for AI?**
No. It's an authorization and audit layer for actions an agent tries to perform. It decides whether a
specific agent may perform a specific action on a specific target, and records the decision.

**Does it stop prompt injection?**
It changes what prompt injection can achieve. Injection can change what the agent *requests*; it cannot change
what the security layer *allows*, because the decision doesn't use the request's claims. It does not stop the
model from being manipulated — it stops the manipulation from turning into an unauthorized action (for actions
routed through the guard).

**Is the audit log immutable?**
No — and we won't say it is. It is **tamper-evident**: modification, insertion, reordering, and tail
truncation are detectable via a sha256 hash chain and a head anchor. An attacker who can rewrite both the log
and its anchor can still erase history. See the threat model.

**Does it do encryption?**
No. `renker-core` defines crypto *interfaces* only and implements none. Cryptography lives in a separate,
audited module (RenkerVault) using established libraries — never home-grown.

**What does it run on / depend on?**
Python ≥ 3.10, **zero runtime dependencies** (standard library only). Dev/test uses pytest, ruff, hypothesis.

**Is it production-ready for a hospital or court?**
It is a strong, tested vertical slice with honestly documented limits. It is **not** externally audited, does
not authenticate actors cryptographically, and currently enforces only file actions routed through the guard.
Those gaps are listed in `claims.md` and the threat model.

**How is it different from OS sandboxing?**
See `docs/comparison.md`. Short version: OS sandboxes constrain a *process*; Renker constrains a *named actor's
specific action* with per-grant scope, expiry, revocation, and an explainable, audited decision.
