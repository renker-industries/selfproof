# renker-core

![License](https://img.shields.io/badge/license-proprietary-red)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![CI](https://github.com/sebastianrenker/renker-core/actions/workflows/ci.yml/badge.svg)
![Dependencies](https://img.shields.io/badge/runtime%20deps-zero-brightgreen)

> A small, deterministic security decision kernel for autonomous AI agents — ALLOW, DENY, or REQUIRE_APPROVAL, explainable and auditable.

## Overview

A dependency-free Python library that answers a single question well: *should
this actor be allowed to perform this action on this resource, right now?* The
answer is a first-class, immutable, serializable `Decision`. The security
decision lives **outside** the LLM by construction.

**Why it exists:** autonomous agents get real capabilities (files, processes,
network). A manipulated agent (prompt injection, a poisoned tool result) can be
talked into harmful actions, and guardrails inside the model can be talked
around. renker-core makes the decision deterministic, capability-scoped,
fail-closed, and recorded — so injection can change *what is requested*, never
*what is allowed*.

## Features

Core primitives (these words are **not** synonyms — a Capability grants
Permissions to a subject; a Policy governs conditions):

| Primitive | Meaning |
|---|---|
| **Identity** | *Who* is asking. Validated, **not** authenticated. |
| **Action** | *What* verb in a namespace, e.g. `Action("filesystem","write")`. |
| **Resource** | *On what*, e.g. `Resource("file","/home/u/x")`. |
| **Capability** | A grant to a subject, scoped, time-bound + revocable. |
| **Permission** | The (Action + ResourcePattern) pair a capability grants. |
| **Policy** | Versioned conditions that can only **restrict**. |
| **Context** | Environment signals; cannot loosen a decision. |
| **Decision** | Immutable, serializable result: effect + subject/action/resource + policy id/version + reason + obligations + timestamp + decision_id. |
| **Approval** | One-time, expiring, replay-protected model for REQUIRE_APPROVAL. |
| **Audit** | Structured, decision-linked, tamper-evident event chain via an `AuditSink`. |

Zero runtime dependencies (standard library only). The public surface is frozen
in `renker_core.__all__` and guarded by `tests/test_public_api.py`.

## Architecture

```
Agent Request -> Identity -> Capability -> Context -> Policy -> Risk -> Decision
                                                                          |
                                                           ALLOW / DENY / REQUIRE_APPROVAL
                                                                          |
                                                               EXECUTE / APPROVAL -> AUDIT
```

`Authorizer` orchestrates the flow (fail-closed). `PolicyEngine` (a `Protocol`)
makes the decision; `StaticPolicyEngine` is the built-in implementation.
RBAC/ABAC/Remote/Composite engines are documented extension points, not built
(see `docs/EXTENSION_POINTS.md`).

**Security model:**

- **Fail closed.** Invalid/expired identity, unknown capability, unauthorized
  resource, expired/replayed approval, unknown policy, or any evaluation error
  resolve to **DENY**. Errors never become ALLOW.
- **Decision is outside the LLM** — reads only trusted grants + actor/action/
  resource/context, never a request-supplied "authorized"/"risk" flag.
- **Least privilege**: capabilities are actor-bound, scoped, time-bound,
  revocable, immutable.
- **Scope safety**: path resolution + `os.path.normcase` — traversal, prefix
  confusion, and case tricks are rejected.
- **Replay protection**: `request_id`/`nonce`/`issued_at` + `ReplayGuard`;
  approvals are one-time, bound to a specific `decision_id` + subject/action/resource.
- **No home-grown crypto**: signature verification is an interface, not an
  implementation. No dummy security, no `return True` in authz code.

Honest non-guarantees: [`docs/THREAT_MODEL.md`](docs/THREAT_MODEL.md),
[`SECURITY_ATTACKS.md`](SECURITY_ATTACKS.md).

**Status / roadmap:** the full primitive set (Identity, Capability, Permission,
Policy, Context, Decision, Risk, Approval, Replay, Audit, Authorizer) is
**CURRENT**; signed identities, RBAC/ABAC/Remote/Composite engines, an
Evidence/Provenance primitive and wire serialization are **PROPOSED** extension
points. The shipped, black-box-verified public subset is
[`renker-core-authz`](https://github.com/sebastianrenker/renker-core-authz)
(Apache-2.0); this repo is the next-generation kernel that will re-supersede it.

## Quickstart

```bash
pip install -e ".[dev]"    # Python >= 3.10, zero runtime dependencies
```

```python
from datetime import datetime, timezone
from renker_core import (
    Identity, Action, Resource, Context, Capability, CapabilityStore,
    PathScope, Policy, StaticPolicyEngine, Authorizer, AuthorizationRequest,
    InMemoryAuditSink,
)

store = CapabilityStore()
store.grant(
    Capability(
        capability="filesystem.write",
        scope=PathScope(base="~/project/drafts"),
        granted_to="agent:session-1",
        granted_by="human:owner",
        issued_at=datetime.now(timezone.utc),
        expires_at=None,
    )
)

authorizer = Authorizer(StaticPolicyEngine(store, Policy("default", "1")), InMemoryAuditSink())
decision = authorizer.authorize(
    AuthorizationRequest(
        subject=Identity("agent", "session-1"),
        action=Action("filesystem", "write"),
        resource=Resource("file", "~/project/drafts/note.md"),
        context=Context(environment="development", user_present=True),
    )
)
print(decision.effect.value, "-", decision.reason)  # ALLOW - within capability scope...
```

## Tests

```bash
ruff format --check . && ruff check . && mypy && pytest -q
```

132 tests: unit, integration (full flow), security (invalid/expired identity,
unknown capability, unauthorized resource, traversal, replay, expired/replayed
approval, malformed input, policy failure), property-based (hypothesis)
invariants, and the tamper-evident audit chain.

## License

Proprietary — "All rights reserved" (see [`LICENSE`](LICENSE)). © 2026 Sebastian
Renker. Confirm or change before any distribution.
