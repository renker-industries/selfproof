# Demo script (3 minutes)

Goal: show that the security boundary is outside the agent, and that every decision is auditable.

## Setup (once)
```bash
git clone <renker-core>
cd renker-core
pip install -e ".[dev]"
```

## Beat 1 — the happy path (20s)
> "An agent is granted one capability: read files under a project folder."

```bash
python examples/protected_agent/protected_agent.py
```
Point at: `ALLOWED READ -> ALLOW | 'hello from the project'`.

## Beat 2 — the attack (30s)
> "Now the same agent — imagine a poisoned web page told it to — asks to read `~/.ssh/config`."

Point at: `DENIED READ -> DENY | target is outside capability scope .../project/**`.
> "The agent *asked*. The policy engine *refused*. The refusal is explainable."

## Beat 3 — the audit (30s)
> "Both attempts are recorded, and the log is tamper-evident."

Point at the printed audit trail and `audit.verify() -> OK`.
> "Edit any past entry and `verify()` raises. That's the accountability layer."

## Beat 4 — why it can't be talked around (40s)
```bash
python -m pytest tests/test_trust_boundary.py -q
```
> "These tests prove the request can't supply its own authorization: no `context`/`risk` input exists,
> capabilities are immutable, and prompt-injection / confused-deputy attempts resolve to DENY."

## Close (20s)
> "Small, deterministic, tested, outside the model. That's the foundation the rest of the platform builds on."

## Full demo variant
`python demo/demo_slice.py` shows allow-write, allow-read-back, deny-ssh, deny-traversal, plus the verified
audit trail.
