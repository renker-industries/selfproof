# Example: a protected agent action

The smallest end-to-end demonstration of the Renker security slice. In under five minutes it shows the value:
an agent's file action is only executed if a capability permits it, and every decision is audited.

```bash
pip install -e ".[dev]"      # from the renker-core repo root
python examples/protected_agent/protected_agent.py
```

## What it shows

```
agent (demo-session)
   │  request: read project/example.txt
   ▼
identity  →  capability (filesystem.read, scope: project/**)
   ▼
policy → ALLOW → file read → audit event

agent (demo-session)
   │  request: read ~/.ssh/config
   ▼
policy → DENY (target outside capability scope) → not executed → audit event
```

Expected output (paths differ per run):

```
ALLOWED READ  -> ALLOW | 'hello from the project'
DENIED READ   -> DENY  | target is outside capability scope .../project/**

Audit trail:
  ALLOW   filesystem.read  success
  DENY    filesystem.read  blocked

audit.verify() -> OK
```

## The point
The agent *requested* both reads. The security layer — not the agent's reasoning — decided. Change the agent
prompt however you like; it cannot widen the capability. That is the whole idea.
