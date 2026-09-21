# Extension points (deliberately not implemented yet)

renker-core is an early-stage kernel. These capabilities have **clean interfaces or clear seams**, but are
**not** implemented — to avoid dummy security. No `return True` in authorization code; no home-grown crypto.

## 1. Signed identities / signature verification
**Status: interface only.** `Identity` is *validated* (well-formed, non-expired) but **not authenticated**.
The caller must supply a trusted `Identity`. To close forged-identity, verify a signed request:

```
Agent --signed request--> renker-core --verify signature--> trusted Identity --> authorize
```

`renker_core/crypto_interface` defines the boundary (`Encryptor`/`Signer`/`Verifier` Protocols). The
implementation belongs in a separate, audited module built on established primitives (libsodium/NaCl, the
`cryptography` package), **never** here. Recommended seam: a `SignatureVerifier` Protocol that the
`Authorizer` calls before trusting `request.subject`; if a request claims to be signed and verification
fails or no verifier is configured, the request must **fail closed** (DENY). This is documented, not stubbed
with a fake verifier.

## 2. Alternative policy engines
`PolicyEngine` is a `Protocol`. `StaticPolicyEngine` is the only implementation. Future engines
(`RBACPolicyEngine`, `ABACPolicyEngine`, `RemotePolicyEngine`, `CompositePolicyEngine`) plug in without
changing the `Authorizer`. Not built until a real consumer needs them — no speculative frameworks.

## 3. Evidence / Provenance
The vision lists `Evidence`. It is **intentionally not implemented** in the current kernel: renker-core's job
is authorization decisions, and there is no consumer yet that needs to attach graded evidence to an
observation. The clean design, when it lands, is a separate primitive:

```
Evidence(evidence_id, source, content_hash, observed_at, collected_by, provenance)
```
with the strict distinction `Observation != Fact` and `Claim != Evidence`. Adding it now would be
over-engineering; this note is the architectural decision to defer it.

## 4. Capability wire serialization / protocol
Cross-process and cross-language use (RenkerVault, Continuum) needs a versioned wire format for capabilities
and decisions. `Decision` is already serializable (`to_dict`/`from_dict`). A signed, versioned capability
token format is deferred to the `protocol` primitive.

## 5. Approval transport
`ApprovalStore` is an in-memory reference implementation with the correct semantics (expiry, one-time
consume, binding to `decision_id` + subject/action/resource). A durable/remote `ApprovalStore` (database,
human-in-the-loop UI) is an extension point with the same interface.
