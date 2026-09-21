# Capability matrix

Generated from `src/selfproof/adapters` by
`scripts/gen_capability_matrix.py`. Do not edit by hand.

Levels: L0 rules-file only (advisory); L1 enforced at commit and in CI;
L2 enforced in-session via native hooks (plus L1).

| Agent | Level | Rules file | Docs checked | Evidence | Notes |
| --- | --- | --- | --- | --- | --- |
| `aider` | L1 | AGENTS.md | no | Enforced by the git+CI floor. Scriptable, many models. | Session-level hooks unverified; declared L1 until its docs are checked. |
| `claude_code` | L1 | CLAUDE.md | no | Enforced by the git+CI floor. Uses CUSTOS as a plugin in the seed stage. | L2 target: port CUSTOS's native Claude Code hooks and prove they block in-session. Not wired/tested yet, so declared L1, not L2. |
| `codex` | L1 | AGENTS.md | no | Enforced by the git+CI floor. Reads the AGENTS.md rules file. | Session-level hooks unverified; declared L1 until its docs are checked. |
| `cursor` | L1 | AGENTS.md | no | Enforced by the git+CI floor. Reads project rules. | Session-level hooks unverified; declared L1 until its docs are checked. |
| `gemini_cli` | L1 | GEMINI.md | no | Enforced by the git+CI floor. Reads the GEMINI.md rules file. | Session-level hooks unverified; declared L1 until its docs are checked. |
| `git` | L1 | — | yes | commit-msg, pre-commit and pre-push hooks under hooks/ run the gates and the Built-by trailer check; CI re-runs the gates on every PR. | The universal enforcement floor; applies to every agent that commits. |
| `ollama` | L0 | — | yes | A model runner, not an agent; no commit or hook integration by itself. | Experimental. Ollama runs models; enforcement needs a wrapper that commits through git (which would raise it to L1). Declared L0 with its limit stated. |
