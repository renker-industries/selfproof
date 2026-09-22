# Selfproof

> Selfproof checks AI-written code for slop and security problems, records
> evidence for every check on a tamper-evident ledger, and builds itself through
> its own gates. Its kernel is `renker-core`.

**Status: bootstrapping (private).** Built by a local agent under a written
[autonomy charter](AUTONOMY_CHARTER.md). Some components in the
[concept](docs/CONCEPT.md) are still `planned`.

## Download

**Windows — [⬇ Download Selfproof_Setup.exe](https://github.com/renker-industries/selfproof/releases/latest)**
Run the installer, no Python needed. Double-click Selfproof and the dashboard opens.

**macOS / Linux —** [⬇ download the binary](https://github.com/renker-industries/selfproof/releases/latest),
or install with one line:

```bash
curl -fsSL https://raw.githubusercontent.com/renker-industries/selfproof/main/install.sh | sh
```

**Windows PowerShell (one line):**

```powershell
irm https://raw.githubusercontent.com/renker-industries/selfproof/main/install.ps1 | iex
```

**Phone —** open the dashboard page and choose "Add to Home Screen". More in
[running as an app](docs/guides/desktop.md). Until the project is public, these
downloads work for people with repository access.

## Why it is different

Most "AI guardrails" ask the model to behave. Selfproof does not trust the
model: it runs deterministic gates in git and CI, and every result is bound to
an exact commit and written to a hash-chained ledger anyone can recompute.

- **Deterministic kernel.** `renker-core` decides allow/deny/approve,
  independent of any model.
- **Enforced for every agent.** Git hooks and CI apply no matter which agent
  wrote the code (Claude Code, Codex, Gemini CLI, Cursor, Aider).
- **Evidence, not adjectives.** No "secure" without a check behind it. The
  strongest claim allowed is "0 known findings at commit X per tools Y on date Z".
- **It builds itself, honestly.** Failed self-build attempts are shown as
  plainly as successes.

## What it promises (and nothing more)

1. Every "done"/"correct"/"secure" statement is bound to an executed check on the
   exact commit.
2. Every check leaves a tamper-evident ledger entry anyone can verify.
3. Each release has zero known open findings of medium+ severity, per named
   tools, versions and date.
4. Every self-claim is evidence-linked or labelled `planned`.

It never claims "absolutely secure", "unhackable" or "bug-free". See
[SECURITY.md](SECURITY.md).

## Use it on your project (with any AI)

Selfproof does not write code — your AI does. It gives every AI the same rules
and checks whatever it produces. **One command sets everything up:**

```bash
cd your-project
selfproof start   # auto-sets-up (rules for every AI + checks), checks, opens the dashboard
```

That is the whole setup — no `init` step to run yourself. After that you **only
talk to your AI in its terminal** and Selfproof runs on its own:

- Claude Code checks automatically when it finishes (an installed
  `.claude/settings.json` Stop hook).
- Any AI is checked automatically when it commits (git hooks).

Each AI reads the rules file Selfproof wrote — Claude Code → `CLAUDE.md`,
Codex/Cursor/Aider → `AGENTS.md`, Gemini CLI → `GEMINI.md`. See
[QUICKSTART.md](QUICKSTART.md) or the
[full walkthrough](docs/guides/using-with-any-ai.md).

## Command reference (short)

```bash
selfproof build           # run the enabled gates against the current commit
selfproof ledger verify   # recompute the tamper-evident evidence chain
selfproof dashboard open  # open the evidence dashboard in your browser
```

No typing needed for the dashboard: the packaged binary opens it when you
double-click it.

## The gates

`language`, `proof`, `slop`, `architecture`, `test_weakening`, `docs_coverage`,
`docs_claims`, `security` — each with a known-bad / known-good corpus, so the
gates themselves are tested. Details in
[docs/reference/gates/](docs/reference/gates/).

## How self-building works, honestly

An AI agent (by default Claude Code, run locally) writes each change on a branch.
Selfproof's own gates check it and record evidence. Changes to the gates, the
kernel and other protected paths always need a human. The model writes the code,
the gates check it, and a human owns the rules. More in
[docs/explanation/how-self-building-works.md](docs/explanation/how-self-building-works.md).

## Where it comes from

| Part | Source |
| --- | --- |
| Kernel (`renker-core`) | the owner's own decision kernel |
| Gate engine, fleet mode | the owner's CUSTOS, split into a neutral core |
| Token layer | the owner's RENKER FLINT |
| External scanners (optional) | gitleaks, osv-scanner, zizmor (orchestrated, never bundled) |

## License

New code is Apache-2.0 ([LICENSE](LICENSE), [NOTICE](NOTICE)). The imported
kernel `src/renker_core/` stays proprietary until relicensing is executed.
