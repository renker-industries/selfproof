# Use Selfproof with any AI

Selfproof does not write code — your AI does. Selfproof gives every AI the same
rules and checks whatever it produces, so the result is the same no matter which
assistant you use.

## In one sentence
Run `selfproof init` in your project, code with any AI, and let the gates check
each change.

## Set it up (once per project)

```bash
cd your-project
selfproof init
```

This writes:

- `CLAUDE.md`, `AGENTS.md`, `GEMINI.md` — the rules each AI reads. Claude Code
  reads `CLAUDE.md`; Codex, Cursor and Aider read `AGENTS.md`; Gemini CLI reads
  `GEMINI.md`. They are generated from `rules/agents.yaml`, so you edit one file
  and regenerate with `selfproof rules generate`.
- `selfproof.toml` — which gates run and your test command. Edit
  `proof.commands` to match your project (e.g. `pytest`, `npm test`).
- git hooks — the gates run at commit and push automatically.

## The daily loop

1. **Code with any AI.** It reads its rules file and follows the same rules.
2. **Check the change:** `selfproof build`. Each gate reports `PASS`, `FAIL` or
   `SKIPPED`. The hooks also run this at commit and push.
3. **See the evidence:** `selfproof dashboard open`. It shows how many checks
   ran, what was prevented, and the self-built share.
4. **Verify anytime:** `selfproof ledger verify` recomputes the tamper-evident
   chain.

## What each gate checks in your project

By default `init` enables the gates that fit any project: `language`
(English-only), `proof` (your tests/lint), `slop` (AI slop in Python),
`security` (secrets, forbidden dependency licenses, workflow hardening) and
`test_weakening` (removed tests or added skips vs `main`). Add or remove gates in
`selfproof.toml` under `[gates] enabled = [...]`.

## What it does not do
It does not run the AI for you, and it does not fix the code — it checks it and
records evidence. A `FAIL` means fix the change; a missing tool shows as
`SKIPPED`, never a false pass.
