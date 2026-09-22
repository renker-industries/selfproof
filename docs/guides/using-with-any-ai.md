# Use Selfproof with any AI

Selfproof does not write code — your AI does. Selfproof gives every AI the same
rules and checks whatever it produces, so the result is the same no matter which
assistant you use.

## In one sentence
Run `selfproof init` in your project, code with any AI, and let the gates check
each change.

## The fastest way

```bash
cd your-project
selfproof start
```

`start` sets the project up automatically on first use, checks your code, and
opens the dashboard. `selfproof build` does the same auto-setup on first run, so
you never have to run `init` by hand. The rest of this page explains what that
setup contains.

## Set it up explicitly (optional)

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

## The daily loop — hands off

You only talk to your AI in its terminal. Selfproof runs on its own:

- **Claude Code** checks automatically when it finishes a response, because
  `init` writes a `.claude/settings.json` Stop hook that runs the fast static
  gates. If something fails, Claude sees it and can fix it before you continue.
- **Any AI** (Claude Code, Codex, Cursor, Aider, Gemini CLI) is checked
  automatically when it commits, through the git hooks — the full gate set at
  push.

So the flow is just: *type your request to the AI → it codes → Selfproof checks
by itself*. The `selfproof` binary must be on your PATH (the installer adds it).

You can still run it by hand anytime:

- `selfproof build` — run the gates now.
- `selfproof dashboard open` — see how many checks ran and what was prevented.
- `selfproof ledger verify` — recompute the tamper-evident chain.

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
