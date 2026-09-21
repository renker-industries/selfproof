# RENKER_PLATFORM_AUDIT

- **Date:** 2026-08-10
- **Phase:** Phase 2, steps 1–2 (audit + gap report). **No application code was changed in this step.**
- **Method:** Source inspection of all four repos (README, wiki, ADRs, tests, CI, manifests, source structure, security and release configuration). Documentation was **not** equated with implementation.

Legend: **IMPLEMENTED** (code present + used) · **PARTIAL** (partial code) · **EXPERIMENTAL** (prototype, expressly unfinished) · **DOC-ONLY** (only described) · **PLANNED** (roadmap only).

---

## Portfolio map

### renker-core (private)
```
renker-core
├── implemented   : package scaffold; 10 importable primitives as constant placeholders;
│                   crypto_interface as pure Protocol types; CI (ruff+pytest); one smoke test
├── tested        : smoke test only (import + constants). No logic tested, because no logic exists.
├── experimental  : —
└── planned/doc   : Identity, Capabilities, Permissions, Policy, Audit, Events, Memory, Tasks,
                    Experiments, Evidence, protocol — all DOC-ONLY (Vision + wiki), no logic
```
**Maturity: skeleton.** The value so far lies in structure and documentation, not in function.

### rencora (public) — ACT
```
rencora
├── implemented   : PyQt6 desktop agent; tool dispatch (agents/router.py); ~25 actions/;
│                   core/policy.py (risk levels 0..6, confirmation gate, safe default);
│                   prompt-injection trust boundary (wrap_external); audit log (core/policy.audit,
│                   logs/audit.log with rotation); path-traversal protection (file_controller._is_safe_path,
│                   home-root-based); DPAPI secret encryption (core/dpapi.py, core/secrets.py);
│                   encrypted remote control (AES-256-GCM), login rate limit, firewall pinning
├── tested        : 7 security tests: test_permissions, test_filesystem_security,
│                   test_audit_rotation, test_desktop_sandbox, test_prompt_boundary,
│                   test_upload_filename, test_tunnel_integrity; CI build.yml (+ new release-windows.yml)
├── experimental  : RencoraLM v3 connection, gesture control, proactive engine
└── planned/doc   : fine-grained, actor-bound capabilities with scope/expiry/revocation (missing)
```
**Maturity: the strongest, most production-ready repo.** Security is real, tested, and honestly documented.

### renkervault (public + local) — SECURE
```
renkervault
├── implemented   : Tauri desktop client (TS/React); E2E crypto on @noble/* (primitives, ratchet,
│                   pq/post-quantum, padding, vault, safety); Node relay server; deploy (Caddy/systemd/Tor);
│                   Inno Setup installer; shipped release v0.1.0 (NSIS+MSI)
├── tested        : client/tests/security, server/tests/security
├── experimental  : prototype status per README (not an externally audited product)
└── planned/doc   : versioned protocol v1, fuzzing, external crypto review
```
**Maturity: a working crypto prototype with a security focus.**

### continuum (public, MIT) — LEARN
```
continuum
├── implemented   : phase-0 research pipeline in src/continuum/ (memory, worldmodel, hypothesis,
│                   learning, verification, eval, safety, llm, data); demo-loop script
├── tested        : 10 tests (hypothesis, verification, worldmodel, memory_store, eval_metrics,
│                   governance, consolidation, simulated_lab, speed1); CI ci.yml (ruff+pytest+demo smoke)
├── experimental  : the entire "research" runs against a SIMULATED objective function, not real hardware
└── planned/doc   : real experiments, independent reproduction, validated results
```
**Maturity: a clean phase-0 state, honestly marked as a prototype.**

---

## The 12 questions

**1. What does each repo really do today?**
- renker-core: nothing functional — an importable scaffold + docs.
- rencora: a runnable desktop AI agent that performs real system actions, with tool-risk-based approval, a trust boundary, an audit log, and home-root path protection.
- renkervault: an E2E-encrypted chat client + relay, with vetted crypto libraries.
- continuum: a reproducible but simulated research learning loop.

**2. Strongest existing functionality?**
rencora's security layer (`core/policy.py` + the 7 security tests). It is real, tested, and honest. It is the natural docking point for platform security.

**3. Which parts of renker-core are actually reusable?**
Currently: the **structure and naming** of the primitives and the `crypto_interface` protocols. **No** logic code is reusable, because none exists. The constants (`RISK_TIERS`, `APPROVAL_POLICIES`, `CHAIN_HASH_ALGORITHM` …) are usable as vocabulary.

**4. Which proposed core abstractions are premature?**
`memory`, `tasks`, `events`, `experiments`, `evidence`, `protocol` (wire format). They solve no real problem of rencora today. `capabilities`, `permissions`, `policy`, `audit`, `identity` are justified, because rencora lacks exactly the fine-grained, actor-bound authorization.

**5. Architecture boundaries?**
- renker-core: a language/process-neutral authorization foundation, stdlib-only, **no** app logic, **no** crypto implementation.
- rencora: execution + UI + LLM; consumes authorization.
- renkervault: transport/identity crypto; the only place for a crypto implementation.
- continuum: research; isolated.

**6. Which repo dependencies are real today?**
Practically **no** code dependency. The only real coupling is documentary (`RENKER_PLATFORM.md`, wikis).

**7. Which dependencies are only conceptual?**
renker-core → (rencora/renkervault/continuum): conceptual. The shared `protocol` layer, shared memory/evidence: conceptual.

**8. Existing security assumptions?**
- rencora: a local, trusted user; the home directory as a coarse trust boundary; tool results from external sources are untrusted; confirmation from risk 4 up; secrets DPAPI-bound.
- renkervault: the server is untrusted (content-blind goal); crypto only from vetted libs.
- renker-core: no enforced assumptions so far (no enforcement code).

**9. Which tests exist?**
rencora 7 security tests; continuum 10 tests + demo smoke; renkervault client/server security suites; renker-core 1 smoke test. CI in all four.

**10. What is missing before production use?**
For the platform authorization: a real, tested Identity→Capability→Policy→Audit chain; adversarial tests (traversal/prefix/expiry/actor/op/target/revocation/audit integrity); a real integration into exactly one rencora action; an honest threat model.

**11. Smallest useful integration renker-core ↔ Rencora?**
An **actor-bound, scope-limited file capability** for **exactly one** file action (read/write): renker-core identifies the actor (agent session), checks the capability (path scope, expiry, revocation), evaluates the policy (ALLOW/DENY/REQUIRE_APPROVAL with an explainable reason), and writes a structured audit event — **above** rencora's existing tool-risk gate, not as a replacement. Least privilege: "may write to `~/Documents/drafts/**`", not "has filesystem access".

**12. What should explicitly NOT be built yet?**
Memory, Tasks, Events, Experiments, Evidence, the `protocol` wire format, any crypto implementation, REQUIRE_APPROVAL UI flows, distributed/server-side audit, network/browser/camera capabilities, microservices, generic `utils` abstractions. Also not: a rewrite of rencora's existing `policy.py` or `file_controller.py`.

---

## Consequence for phase 2

The first vertical slice (Vision default) fits the existing architecture and is implemented — **stdlib-only in renker-core**, with real file execution in the integration adapter and an additive, CI-safe connection to rencora. Details: `docs/THREAT_MODEL.md`, `SECURITY_ATTACKS.md`, `PHASE_2_REPORT.md`.
