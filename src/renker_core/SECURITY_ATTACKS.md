# SECURITY_ATTACKS — renker-core vertical slice

The security boundary is **empirically testable**. Every attack below has an executable
regression test in [`tests/test_security_attacks.py`](tests/test_security_attacks.py) (unless noted).
Run them with `pytest -q tests/test_security_attacks.py`.

The loop for each feature is: builder implements → attacker attempts bypass → failure discovered →
regression test added → fix → repeat. Below, each row is a bypass that is **currently blocked**,
with the test that proves it.

| # | Attack | Attacker goal | Expected | Regression test |
|---|---|---|---|---|
| 1 | **Path traversal** — `drafts/../secret.txt` | escape the scoped directory | DENY, not executed | `test_attack_path_traversal` |
| 2 | **Prefix confusion** — scope `Documents`, target `Documents2/x` | reuse a scope for a sibling dir with a shared string prefix | DENY | `test_attack_prefix_confusion` |
| 3 | **Expired capability** | use a grant past its `expires_at` | DENY (`reason` contains `expired`) | `test_attack_expired_capability` |
| 4 | **Wrong actor (confused deputy)** — agent B uses agent A's grant | act under someone else's authority | DENY | `test_attack_wrong_actor` |
| 5 | **Wrong operation** — read grant, write attempt | escalate read→write | DENY | `test_attack_wrong_operation` |
| 6 | **Wrong target** — grant for `drafts`, request `elsewhere` | act outside the granted path | DENY | `test_attack_wrong_target` |
| 7 | **Revocation mid-lifetime** | keep using a capability after it is revoked | DENY (`reason` contains `revoked`) | `test_attack_revocation_mid_lifetime` |
| 8 | **Malformed actor identity** — `agent` + `../../etc/passwd` | smuggle a path into the actor id | `IdentityError` at construction | `test_attack_malformed_actor_is_rejected` |
| 9 | **Silent decision (no audit)** | perform an action without leaving a trace | every allow/deny emits exactly one audit event; chain verifies | `test_every_decision_produces_audit_event` |
| 10 | **Audit modification** | edit a recorded reason after the fact | `verify()` raises (hash mismatch) | `test_detects_modified_entry` (`test_audit.py`) |
| 11 | **Audit tail truncation** | drop the last decisions | `verify()` raises (head anchor mismatch) | `test_detects_tail_truncation` (`test_audit.py`) |
| 12 | **Audit full deletion** | empty the log but keep the anchor | `verify()` raises | `test_detects_full_deletion` (`test_audit.py`) |
| 13 | **Policy bypass via no grant** | act with no capability at all | DENY (safe default) | `test_deny_no_capability` (`test_policy.py`) |

## Hardening pass (regulated-use robustness)

Additional attacks/edge cases, with tests in `tests/test_hardening.py`, `tests/test_properties.py`, and
`tests/test_acceptance_regulated.py`:

| # | Attack / edge case | Expected | Test |
|---|---|---|---|
| 14 | **Windows case trick** — scope `Documents`, target `documents/x` | ALLOW on case-insensitive FS (same dir), `Documents2` still DENY | `TestScopeHardening::test_windows_case_insensitive_same_dir_allowed`, `test_prefix_confusion_still_blocked_after_normcase` |
| 15 | **Empty/whitespace scope** | rejected at construction | `test_empty_base_rejected`, `test_whitespace_base_rejected` |
| 16 | **Control chars in actor id** (`\x00`, `\n`, `\x1b`) | `IdentityError` | `TestIdentityHardening::test_control_characters_rejected` |
| 17 | **Empty / None action or target** | DENY, no crash | `test_empty_action_denied`, `test_none_action_denied_without_crash`, `test_permits_rejects_empty_target` |
| 18 | **Concurrent audit appends** (8×50 threads) | chain stays valid + verifies | `TestAuditHardening::test_concurrent_appends_keep_chain_valid` |
| 19 | **Audit reordering** | `verify()` raises | `test_reordering_detected` |
| 20 | **Corrupt audit line** | `AuditError`, not a raw parse error | `test_corrupt_line_raises_audit_error` |
| 21 | **Fuzzed scope containment** (400 examples) | `permits` never diverges from `is_relative_to` ground truth | `test_permits_never_diverges_from_ground_truth` |
| 22 | **Fuzzed single-byte audit mutation** (150 examples) | every mutation detected | `test_any_single_byte_mutation_is_detected` |
| 23 | **Malformed enforcement config** (rencora) | fail **closed** (deny), never open | rencora `test_file_controller_guard::test_malformed_config_fails_closed` |
| 24 | **Cross-tenant isolation** (hospital: Dr. A's agent → Dr. B's patient) | DENY, audited | `test_acceptance_regulated::test_hospital_per_patient_isolation` |

## Known, documented limitations (attacks NOT closed)

These are intentionally out of scope for this slice and are stated honestly in `docs/THREAT_MODEL.md`:

- **Forged trusted actor.** The caller supplies the `Actor`. renker-core validates its shape and
  matches `granted_to`, but does not cryptographically authenticate it. A caller that fabricates a
  trusted `Actor` is not stopped here.
- **Replay within lifetime.** A valid capability may be reused until it expires or is revoked; there is
  no per-use nonce.
- **Full host compromise.** An attacker who can rewrite **both** the audit log and its `.head` anchor
  can erase history undetectably. The chain is *tamper-evident*, not *tamper-proof*.
- **Bypassing the guard.** Enforcement applies only to actions routed through `GuardedFilesystem`.
  Direct OS calls are not constrained by renker-core.

New bypasses discovered in future sessions should be added here **with a failing test first**, then fixed.
