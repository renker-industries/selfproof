# RENKER — Trusted Infrastructure for Autonomous AI
**Concept document v1.0**
As of: 9 August 2026 · Author: Sebastian Renker · Developed with Claude

> **Note on the factual basis:** This document is based on the project properties of Rencora, Continuum, and RenkerVault as you described them, and on the previous joint analysis. Concrete repository details (code, file structure, commit history) were not re-verified in this session. All technical proposals below should be read as **target architecture / proposal**, not as an inventory of the current code. Before Claude Code works on it, the actual current state of the three repos should be reconciled against this document (see section 14).

---

## 0. Executive Summary

Renker is not a portfolio of three independent projects, but a platform with one thesis:

> **The next generation of AI systems will not be measured by how intelligent it is, but by how controllable, auditable, and trustworthy it is when acting on its own.**

Three product pillars serve this thesis from different directions:

| Pillar | Role | Core question |
|---|---|---|
| **Rencora** (ACT) | Agent runtime with capability security | What may an agent do, and how is that enforced? |
| **RenkerVault** (SECURE) | Identity and secure-communication layer | Whom can an agent trust, and how does data stay protected? |
| **Continuum** (LEARN) | Autonomous research and discovery engine | How does observation become verified knowledge — without selling hallucination as fact? |

All three share a common foundation, **`renker-core`**, which does not contain the products' business logic but the shared primitives: Identity, Permissions, Memory, Events, Tasks, Experiments, Evidence, Audit.

Commercially, the strongest short-term lever is not in the consumer space, but in **agent security for enterprises** — a market that is only just emerging with the spread of autonomous AI agents. The business model is B2B/SaaS with tiered plans; realistic target sizes are in the low to mid single-digit millions ARR with 100–500 paying companies — not millions of end users.

The next milestone is not a revenue target. It is: **a single independent user who voluntarily pays.**

---

## 1. The vision

**Guiding statement:**

> *Renker builds infrastructure for AI systems that can act, learn and communicate without requiring blind trust.*

The central question of the next AI generation is no longer primarily "How intelligent is the model?", but:

> "How much may this system do on its own, and how can we trust it while it does?"

This is exactly where the three projects meet. Rencora gives agents the ability to act *within controlled boundaries*. RenkerVault ensures that communication between human, agent, and service is not compromisable in the process. Continuum ensures that a learning system does not uncontrollably perpetuate its own outputs as truth.

The company behind it is called **Renker** — not Rencora. Rencora is a product of the Renker company, not a synonym for it.

```
                         RENKER
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
       RENCORA         CONTINUUM       RENKERVAULT
          │                │                │
        ACT              LEARN           SECURE
          │                │                │
          └────────────────┼────────────────┘
                           │
                           ▼
                TRUSTED AI INFRASTRUCTURE
```

---

## 2. Platform architecture — big picture

```
                    RENKER PLATFORM
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
    Identity            Security            Memory
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
             ┌─────────────┼─────────────┐
             │             │             │
          Rencora       Continuum    RenkerVault
             │             │             │
           ACT           LEARN         SECURE
```

The dividing line is important: the three products share **primitives**, not **business logic**. Rencora knows nothing of Continuum experiments, Continuum knows nothing of Rencora tool calls. But both speak the same vocabulary for "Who am I", "What may I do", "What happened", and "What is substantiated".

This prevents two typical mistakes when building a platform from several projects:

1. **Monolith trap** — cramming everything into one app, so that each product loses focus and releases block each other.
2. **Silo trap** — three completely separate codebases reinventing security and identity concepts three times differently (and three times error-proneness).

---

## 3. The three pillars in detail

### 3.1 Rencora → ACT: Agent runtime with capability security

**Positioning:** Not "another AI assistant" (a saturated market), but:

> *A personal AI agent that can actually operate your computer — while being controlled by explicit security boundaries.*

```
                 RENCORA
                    │
        ┌───────────┼───────────┐
        │           │           │
       THINK       SEE         ACT
        │           │           │
       LLM       Vision      Tools
        │           │           │
        └───────────┼───────────┘
                    │
               PERMISSION
                  LAYER
                    │
             ┌──────┴──────┐
             │             │
          Allowed       Blocked
             │
             ▼
            OS
```

The differentiating building block is **capability security**: Rencora never holds blanket "terminal access" or "filesystem access". Every capability is an individually granted, individually revocable object:

```
Agent
 │
 ├── filesystem.read      (scope: ~/Documents/**)
 ├── filesystem.write     (scope: ~/Documents/drafts/**)
 ├── process.execute      (scope: allowlist of binaries)
 ├── network.request      (scope: allowlist of domains)
 ├── browser.control      (scope: active tab)
 ├── camera.read          (scope: never without explicit approval)
 └── microphone.read      (scope: never without explicit approval)
```

Every capability carries six properties:

- **Permission** — exactly which action is allowed (not "filesystem", but "read, under this path prefix").
- **Scope** — the concrete boundary (path, domain, process name).
- **Lifetime** — expiry time or session binding; no capability lives forever by default.
- **Audit Trail** — every use is logged, tamper-evidently and traceably.
- **Approval Policy** — automatically allowed, automatically denied, or human approval required, depending on risk.
- **Revocation** — every capability can be instantly revoked at any time, even in the middle of a running action.

An "AI agent" thus becomes a **controllable agent runtime** — and this runtime is the actual product core, independent of which LLM is currently "thinking".

### 3.2 RenkerVault → SECURE: Identity and secure-communication layer

**A hard decision up front:** RenkerVault is not out to replace Signal. The commercial value is not in "we have our own messenger", but in:

> *We build a secure communication and identity layer for agents and humans.*

This makes RenkerVault infrastructure rather than an end-user product:

```
Human
  │
Agent
  │
Service
  │
Device
  │
  ▼
Renker Secure Identity
       │
       ├── E2E encryption
       ├── device identity
       ├── key management
       ├── secure sessions
       ├── metadata minimization
       └── encrypted transport
```

The decisive new use case: RenkerVault secures not only human-to-human communication, but **agent-to-agent and agent-to-human communication**:

```
Rencora on Laptop
       │
       │ encrypted
       ▼
Rencora on Phone
       │
       │ encrypted
       ▼
Rencora Cloud / Relay
```

Design principle: **the server gets as little trust as possible.** Relay nodes should ideally transport ciphertext without seeing content, metadata, or relationship graphs in any usable form.

### 3.3 Continuum → LEARN: Autonomous research and discovery engine

**Positioning deliberately modest:** not "AGI", but:

> *Autonomous Research & Discovery Engine.*

The pipeline:

```
Observation → Memory → World Model → Hypothesis Generation
    → Experiment Design → Execution → Measurement
    → Verification → Knowledge Update → (next iteration)
```

The most important building block is an **evidence-status model** that prevents the system from ever storing its own hallucinations as "knowledge":

```
HYPOTHESIS
    │
    ├── proposed                    (not yet checked)
    ├── simulated                   (tested in the model)
    ├── experimentally tested       (tested for real, once)
    ├── independently reproduced    (confirmed by an independent run)
    └── validated                   (dependable, referenceable)
```

Every claim in the system visibly carries its evidence status. A "proposed" result may never be presented or reused like a "validated" result — this is a hard system rule, not a recommendation.

---

## 4. The shared foundation: `renker-core`

### 4.1 Why a fourth repository

Rencora, RenkerVault, and Continuum should **not** build their own, incompatible versions of "Who am I", "What is allowed", and "What happened". A fourth repository, `renker-core`, becomes the shared foundation — not another end-user product, but a library/service that the three products develop against.

```
renker-core/
├── identity/          # who an actor is (human, agent, device, service)
├── capabilities/       # capability definitions & schemas
├── permissions/         # policy evaluation, approval flows
├── events/               # event bus / event log (append-only)
├── memory/                # shared memory model (episodic/semantic)
├── tasks/                  # task/job representation across all products
├── audit/                   # tamper-evident audit log, query API
├── policy/                    # policy engine (risk rules, approval rules)
├── crypto-interface/            # INTERFACES ONLY, no crypto implementation
└── protocol/                      # wire format between products/devices
```

Usage:

```
Rencora     ↓ renker-core
Continuum   ↓ renker-core
RenkerVault ↓ renker-core
```

### 4.2 The nine shared primitives

| Primitive | Purpose | Used by |
|---|---|---|
| **Identity** | A unique, verifiable identity for human, agent, device, service | all three |
| **Permissions** | The capability model from section 3.1, generically usable | Rencora primarily, Continuum for tool access |
| **Memory** | Episodic + semantic memory with source references | Rencora, Continuum |
| **Events** | Append-only event log as the backbone for audit and reactivity | all three |
| **Tasks** | A uniform representation of "something to be done" | all three |
| **Experiments** | Structure for hypothesis → design → execution → result | primarily Continuum |
| **Evidence** | The status model from section 3.3, but generic: Rencora actions too can be "substantiated" or "unsubstantiated" | all three |
| **Security** | Threat model, sandbox boundaries, crypto interfaces (not the implementation itself) | primarily RenkerVault |
| **Audit** | Tamper-evident, queryable log of every security-relevant action | all three |

### 4.3 The crypto boundary — deliberately *not* part of Core

An important design decision: **the cryptography implementation does not simply move into the shared Core package.** `renker-core/crypto-interface` defines interfaces only (e.g. "encrypt this payload for this recipient", "verify this signature"). The actual cryptographic implementation stays:

- in its own minimal, auditable module (ideally under RenkerVault or a dedicated `renker-crypto` repo),
- built on established, vetted primitives (e.g. libsodium/NaCl, Signal-protocol building blocks) rather than an in-house design,
- with its own, stricter review process than the rest of the platform.

Rationale: if you mix cryptography with general platform logic, every later change to Core automatically becomes a security-critical event. The separation keeps the attack surface for crypto bugs small and makes external audits realistically cheaper.

---

## 5. Agent security as a standalone product

This is potentially the economically strongest short-term building block of the entire platform.

**The core problem:** AI agents are getting more and more permissions. What happens when an agent is manipulated?

```
Website → Prompt Injection → AI Agent → Tool Call → "Upload ~/.ssh/"
```

**The platform's answer:**

```
REQUEST → POLICY ENGINE → Risk Assessment → Permission
   → Sandbox → Execution → Audit
```

For dangerous actions:

```
Agent: "Delete database"
Policy: HIGH RISK
→ DENY   or   → HUMAN APPROVAL
```

### 5.1 Sketch of a permission object (proposal, not current state)

```json
{
  "capability": "filesystem.write",
  "scope": "~/Documents/drafts/**",
  "grantedBy": "user:sebastian",
  "grantedTo": "agent:rencora-session-8f2c",
  "issuedAt": "2026-08-09T10:00:00Z",
  "expiresAt": "2026-08-09T11:00:00Z",
  "approvalPolicy": "auto",
  "riskTier": "low",
  "revocable": true,
  "auditRequired": true
}
```

### 5.2 Sketch of an audit-log entry

```json
{
  "eventId": "evt_9a31...",
  "timestamp": "2026-08-09T10:14:02Z",
  "actor": "agent:rencora-session-8f2c",
  "action": "filesystem.write",
  "target": "~/Documents/drafts/report.md",
  "capabilityRef": "cap_5521...",
  "riskAssessment": "low",
  "decision": "allowed",
  "outcome": "success",
  "chainHash": "sha256:..."
}
```

Such a log should be **append-only** (cryptographically chained, e.g. via a hash chain), so that even a compromised agent cannot silently erase its own traces after the fact.

### 5.3 Risk levels as the basis of the policy engine

| Risk level | Example actions | Default behavior |
|---|---|---|
| **Low** | Read a file in an allowed scope, web research in an allowlist | automatically allowed, logged |
| **Medium** | Write a file outside known scopes, contact a new domain | automatically allowed with a warning, or approval per policy |
| **High** | Access to credentials/keys, delete operations, payment triggering | human approval generally required |
| **Critical** | Access to `.ssh`, production databases, irreversible deletion | denied by default, only with an explicit override |

This building block could in perspective become a standalone product: **Renker Agent Security** — *security layer for autonomous AI agents.* This is probably more commercially interesting than a consumer messenger, because the damage it prevents is immediately measurable in euros (see section 7).

---

## 6. Product portfolio

| Tier | Product | Audience |
|---|---|---|
| **Free / Open Source** | Rencora Core, RenkerVault Protocol, Continuum Research Framework | Community, research, reputation, trust through transparency |
| **Developer** | Renker SDK (Capabilities → Policy → Secure Execution → Audit as building blocks) | Developers who want to build their own agents securely |
| **Enterprise** | Renker Agent Security Platform: agent identity, permissions, sandboxing, policy engine, audit, secret management, secure communication, deployment, compliance | Companies with production AI agents |
| **Research** | Continuum Research Platform: hypothesis generation, experiment planning, scientific memory, verification, evaluation, human oversight | Institutions, labs, research teams |

The open-source tier is not a by-product but strategic: it creates trust (code is inspectable), reputation (community, visibility), and a funnel into the commercial tiers.

---

## 7. Business model

**Basic principle:** B2B rather than a consumer mass market. No race for millions of users and advertising revenue.

| Tier | Price | Audience |
|---|---|---|
| Developer | €0–49 / month | Individual developers, small projects |
| Pro | €100–500 / month | Small teams, startups |
| Business | €1,000–10,000 / month | Mid-sized companies with production agents |
| Enterprise | custom contracts | Large organizations, compliance requirements |
| Research | custom contracts | Institutions, labs |

**Illustrative calculations (target scenarios, expressly not forecasts):**

```
100 companies × €2,500 / month = €250,000 MRR ≈ €3M ARR
500 companies × €5,000 / month = €2.5M MRR ≈ €30M ARR
```

**The actual value driver:** a security incident that the platform prevents typically costs a company a multiple of the license cost — for instance when an autonomous agent accidentally loses data, exposes secrets, publishes code, compromises credentials, or manipulates internal systems. This avoided damage is the actual business case, not the feature list.

**An important honesty caveat:** These numbers are target sizes to put the order of magnitude in context, not a dependable financial plan. A real forecast needs market validation (section 10, months 7–12), not a top-down calculation.

---

## 8. Scientific integrity for Continuum

Continuum must never be marketed with an "AGI" claim. Instead, a strict scientific protocol applies to every output:

- **Benchmarks** against recognized, publicly reproducible baselines.
- **Ablations** that show which system component has which effect.
- **Reproducibility** as a mandatory criterion, not a bonus — no result counts that cannot be run again.
- **Blind evaluation**, where possible, to avoid confirmation bias.
- **Independent replication**, before a result reaches the status "validated" (see the evidence model, section 3.3).

Only when Continuum demonstrably finds better experiments than human or classical baselines under an identical budget does the strategic situation change fundamentally — with application fields such as materials science, chemistry, pharma, energy, optimization, engineering, and simulation. Until then, Continuum is deliberately the slowest, scientifically strictest of the three building blocks.

---

## 9. Prioritization of the three pillars

| Rank | Project | Role | Rationale |
|---|---|---|---|
| 🥇 | **Rencora** | Agent Security | short-term product candidate with a clear, measurable business case |
| 🥈 | **RenkerVault** | Security Foundation | infrastructure rather than a consumer product; backs Rencora, not the other way around |
| 🥉 | **Continuum** | Research / Moonshot | the largest long-term lever, but must grow scientifically, slowly and cleanly |

---

## 10. Roadmap — 12 months

### Months 1–3: Foundation

**Rencora**
- Capability/permission system (schema, storage, checking)
- Sandboxing for tool execution
- Audit log (append-only, queryable)
- First prompt-injection test suite

**RenkerVault**
- Protocol specification (written, versioned)
- Threat model (explicitly documented, with out-of-scope statements)
- Test vectors for the crypto layer
- Fuzzing setup
- External or at least structured internal crypto review

**Continuum**
- Define a benchmark suite
- Establish baselines
- Reproducible experiment pipeline
- Evaluation framework (incl. evidence-status fields)

*Definition of Done for month 3:* All three repos have a runnable, testable minimal system along the points above — not "finished", but demonstrable.

### Months 4–6: Stabilization

- **Rencora:** security-first agent runtime — permission system and sandbox work together, no longer in isolation.
- **RenkerVault:** stable protocol v1, frozen for external reviews.
- **Continuum:** first reproducible research benchmarks, published (even if the results are still modest — reproducibility counts more than impressiveness).

### Months 7–9: Test reality

The most important transition in the whole plan: from internal building to external feedback.

- Real external users, not friends, not just GitHub stars.
- People with real problems of their own who test the system on their own use cases.
- Systematic collection of: where does usage break off? What would someone pay for? What gets ignored?

### Months 10–12: Set direction

- Evaluation: which part of the platform does someone actually pay for?
- Derive the focus for year 2 from that — presumably Rencora/Agent Security as the commercial core, RenkerVault as its backing, Continuum as a longer-term research line with its own time horizon.

---

## 11. Working with Claude Code — the development machine

The actual leverage lies not only in the product, but in how it is built. Trial-and-error becomes a systematic process:

```
YOU (hypothesis)
   ↓
CLAUDE (implementation)
   ↓
AUTOMATED TESTS
   ├── PASS ──────────────────┐
   └── FAIL                   │
        ↓                     │
   CLAUDE ATTACKER             │
        ↓                     │
   COUNTEREXAMPLE               │
        ↓                     │
   CLAUDE FIX                   │
        └─────────────────────┘
```

For security-critical building blocks (in particular the Rencora permission system and the RenkerVault crypto layer), the loop is extended with roles:

```
Builder Agent → Attacker Agent → Reviewer Agent → Test Generator → Human Decision
```

**Concrete practice for the next sessions with Claude Code:**

1. **Every task gets a clear Definition of Done** before code is written — ideally derived directly from the roadmap in section 10.
2. **Security-relevant changes** (everything under `permissions/`, `capabilities/`, `crypto-interface/`) always go through the Builder→Attacker→Reviewer cycle, never just "Builder→done".
3. **The attacker agent is explicitly tasked to break the feature** — for instance: "Try to bypass a capability boundary with a manipulated website payload." This is something different from a normal code review.
4. **You remain the architect and final decision authority**, especially for policy decisions like "What counts as critical risk?" — that is a product/value decision, not a purely technical one.
5. **This document itself** can be placed as a reference/context file in the repos (e.g. as `RENKER_VISION.md` in `renker-core`), so that Claude Code can fall back on it for implementation decisions instead of reinventing architecture questions in every session.

---

## 12. What is deliberately NOT being done now

- No building of 100 new features at once.
- No training of proprietary foundation models just because it would be possible.
- No own messenger as a WhatsApp competitor.
- No "AGI" claims, not even in a marketing tone.
- No simultaneous selling of ten products.
- No unvetted proprietary cryptography as a differentiator.
- No cramming of all three projects into a monolith.

The focus is the actual resource, not ideas — there are enough of those.

---

## 13. The actual long-term bet

The stronger bet is not that "one of these three repositories gets rich", but that:

> You develop into a founder/engineer who uses AI to research and build technical systems faster than a traditional small team.

Out of this comes not just a project portfolio, but a **research and product machine**. If it becomes a B2B security product with a few million euros ARR, a million-euro company is realistic. If Continuum eventually delivers real, independently reproduced scientific discovery, the order of magnitude could theoretically lie well above that — but that is a scenario for years, not for the next milestone.

The next milestone deliberately stays small and concrete:

```
1 paying, independent user
        ↓
10 customers
        ↓
100 customers
        ↓
a vision becomes a company
```

---

## 14. Concrete next steps

1. **Reconcile the current state against this document.** Go through the three repos (Rencora, Continuum, RenkerVault) and record for each module from section 4.2/4.1: already exists / partially exists / does not exist.
2. **Create `renker-core` as its own repository**, initially only with the primitives that Rencora concretely needs *now* (Identity, Permissions, Audit) — not all nine at once.
3. **For Rencora: implement the permission object from section 5.1 as a real schema** and run the first prompt-injection test suite against it.
4. **Place this document as `RENKER_VISION.md` in the repos**, so that it serves as a shared reference point for future Claude Code sessions.
5. **Break the month-1–3 goals from section 10 down into concrete tickets/tasks**, with a Definition of Done, so that Claude Code can work on them directly.

---

## Appendix A — Glossary

| Term | Meaning |
|---|---|
| **Capability** | An individually grantable, individually revocable action permission of an agent |
| **Scope** | The concrete boundary of a capability (e.g. a path prefix or a domain allowlist) |
| **Evidence status** | Degree of substantiation of a claim: proposed → simulated → experimentally tested → independently reproduced → validated |
| **Policy Engine** | Component that evaluates incoming actions against risk rules and makes Allow/Deny/Approval decisions |
| **Audit Trail** | Tamper-evident, chronological log of security-relevant actions |
| **Primitive** | Shared, cross-product building blocks in `renker-core` (Identity, Permissions, Memory, Events, Tasks, Experiments, Evidence, Security, Audit) |

## Appendix B — Diagram: target architecture of the end state

```
                         RENKER
                           │
                  TRUSTED AI LAYER
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
      ACT                LEARN              SECURE
    RENCORA            CONTINUUM         RENKERVAULT
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                     RENKER CORE
                           │
       ┌───────────────────┼───────────────────┐
       │                   │                   │
    Identity           Policy Engine       Memory
       │                   │                   │
       ├───────────────┬───┴────┬──────────────┤
       │               │        │              │
     Agents          Tools    Devices        Data
       │               │        │              │
       └───────────────┴────────┴──────────────┘
                           │
                     AUDIT / EVIDENCE
```

---

*This document is intended as a living strategy document. It should be updated as soon as real user data, test results, or architecture decisions confirm or refute the assumptions made here.*
