# Security Properties — renker-core

Evidence matrix for the guarded-action slice
(`Identity → Capability → Policy → Decision → Execute/Audit`). This document maps
each claimed property to the **specific tests** that exercise it, and states
honestly which evidence stages have and have **not** been reached.

Read this alongside [`docs/THREAT_MODEL.md`](docs/THREAT_MODEL.md) (scope, actors,
trust boundaries, explicit non-guarantees) and [`SECURITY_ATTACKS.md`](SECURITY_ATTACKS.md).

## Evidence stages

A property is only as strong as the strongest stage it actually reaches:

- **Implemented** — code enforces it.
- **Tested** — a deterministic unit/integration test asserts it.
- **Adversarially tested** — a test drives the *attack* case, not just the happy path.
- **Measured** — a reproducible measurement exists (latency/throughput).
- **Independently reviewed** — an external party validated it.

Status at time of writing: verified locally with `pytest -q` → **132 passed**
(Python 3.12, `hypothesis` installed via `.[dev]`). No property below has reached
**Independently reviewed** — this system has **not** been externally audited.

## Matrix

| Property | Impl. | Tested | Adversarial | Measured | Indep. reviewed | Anchoring tests |
|---|:--:|:--:|:--:|:--:|:--:|---|
| Fail-closed authorization | ✅ | ✅ | ✅ | ❌ | ❌ | `test_none_action_denied_without_crash`, `test_empty_action_denied`, `test_security_failure_never_allows_outside_scope` |
| Capability scoping (least privilege) | ✅ | ✅ | ✅ | ❌ | ❌ | `test_attack_wrong_operation`, `test_write_then_read_denied_without_read_capability` |
| Resource / scope containment | ✅ | ✅ | ✅ (400-example property) | ❌ | ❌ | `test_permits_never_diverges_from_ground_truth`, `test_allow_implies_resource_in_scope`, `test_base_itself_is_permitted` |
| Path traversal resistance | ✅ | ✅ | ✅ | ❌ | ❌ | `test_attack_path_traversal`, `test_double_dot_stacked_traversal` |
| Prefix-confusion resistance | ✅ | ✅ | ✅ | ❌ | ❌ | `test_attack_prefix_confusion`, `test_prefix_confusion_still_blocked_after_normcase` |
| Case correctness (normcase) | ✅ | ✅ | ✅ | ❌ | ❌ | `test_action_case_mismatch_denied`, `test_windows_case_insensitive_same_dir_allowed` |
| Confused-deputy / actor binding | ✅ | ✅ | ✅ | ❌ | ❌ | `test_attack_wrong_actor`, `test_human_kind_with_same_identifier_is_distinct` |
| Expiry enforcement | ✅ | ✅ | ✅ | ❌ | ❌ | `test_expiry_exact_boundary_denies`, `test_attack_expired_capability` |
| Revocation enforcement | ✅ | ✅ | ✅ | ❌ | ❌ | `test_attack_revocation_mid_lifetime`, `test_revoke_then_regrant_new_id_allows` |
| Input validation (identity/scope) | ✅ | ✅ | ✅ | ❌ | ❌ | `test_empty_base_rejected`, `test_whitespace_base_rejected`, `test_control_characters_rejected`, `test_non_string_identifier_rejected` |
| Audit completeness (allow + deny) | ✅ | ✅ | — | ❌ | ❌ | `test_every_decision_produces_audit_event`, `test_denied_action_never_touches_disk` |
| Audit tamper-**evidence** | ✅ | ✅ | ✅ | ❌ | ❌ | `test_any_single_byte_mutation_is_detected`, `test_detects_modified_entry`, `test_detects_tail_truncation`, `test_reordering_detected`, `test_detects_full_deletion`, `test_corrupt_line_raises_audit_error` |
| Concurrency safety (audit chain) | ✅ | ✅ | — | ❌ | ❌ | `test_concurrent_appends_keep_chain_valid` (8 threads × 50) |
| Cryptographic identity / authentication | ❌ | — | — | — | ❌ | interface only — see below |
| Replay protection (per-use) | ⚠️ partial | ✅ (expiry) | ✅ | ❌ | ❌ | see below |
| Host-compromise resistance | ❌ | — | — | — | ❌ | out of scope — see below |
| Prompt-injection *resistance* | ❌ (n/a) | — | — | — | ❌ | out of core scope — see below |

## Properties that are NOT closed (do not market these)

These follow directly from `docs/THREAT_MODEL.md` §4/§6:

- **Cryptographic identity — NOT implemented.** Signature verification is an
  interface (`crypto_interface`), not an implementation. The kernel *validates and
  canonicalizes* an actor and matches it against `granted_to`; it does **not**
  authenticate it. A caller supplying a forged-but-well-formed `Actor` is trusted.
- **Replay — partial, by design.** A valid capability is reusable until expiry or
  revocation (no per-use nonce). Approvals for `REQUIRE_APPROVAL` are one-time and
  bound to a specific `decision_id`; capability *reuse* is intentional, not a
  replay defense. Adversarial coverage exists for expiry/revocation boundaries, not
  for a per-use anti-replay nonce (there is none).
- **Tamper-evidence ≠ tamper-proof.** The sha256 hash chain + separate head anchor
  make modification, insertion, reordering, and tail truncation **detectable** by
  `AuditLog.verify()`. Full deletion is detected **only while the head anchor
  survives**. An attacker who can rewrite *both* the log and the anchor (i.e. owns
  the host account) defeats detection. There is no external anchoring.
- **Host-compromise resistance — NONE.** A fully compromised OS account can delete
  the log + anchor or feed a forged trusted `Actor`.
- **Prompt-injection is not "solved."** The core guarantee is narrow: injection can
  change *what is requested*, never *what the capability permits*. An action the
  policy explicitly **allows** is allowed even if it was requested for a malicious
  reason — the kernel has no semantic-intent check. Injection *mitigation* lives in
  rencora (`policy.wrap_external`), not here.
- **No enforcement outside the guard.** An agent that calls the OS directly,
  bypassing `GuardedFilesystem`, is not constrained. The guarantee is only as good
  as the routing of actions through the guard.

## Measurement status

**Measured (latency): established, single-machine.** Real micro-benchmark numbers
are committed in [`benchmarks/RESULTS.md`](benchmarks/RESULTS.md): a full
authorization decision is **~0.73 ms** on the reference machine (Python 3.12,
Windows/AMD64), dominated by the `Path.resolve()`-based scope check. These are
single-process, single-run figures with no percentile distribution — cite them as
such. The security-property columns above stay `❌` for *Measured* because those
are correctness properties, not timing properties. Reproduce with:

```bash
pip install -e ".[dev]"
python benchmarks/bench.py
```

## Reproducing the evidence

```bash
pip install -e ".[dev]"          # zero runtime deps; hypothesis is a dev dep
ruff format --check . && ruff check . && mypy && pytest -q
```
