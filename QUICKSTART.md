# Selfproof — Quickstart

Three steps. Works with any AI (Claude Code, Cursor, Codex, Aider, Gemini CLI).

## 1. Install

Download the file for your system from the
[Releases page](https://github.com/renker-industries/selfproof/releases/latest)
and run it. On Windows, run `Selfproof_Setup.exe`. Or install with one line:

```bash
# macOS / Linux
curl -fsSL https://raw.githubusercontent.com/renker-industries/selfproof/main/install.sh | sh
```

```powershell
# Windows (PowerShell)
irm https://raw.githubusercontent.com/renker-industries/selfproof/main/install.ps1 | iex
```

## 2. In your project, run one command

```bash
cd your-project
selfproof start
```

That is the whole setup. `start` sets everything up automatically (it writes the
rules files every AI reads and turns on the checks), runs the checks, and opens
the dashboard. You do not run `init` yourself — `start` and `build` set the
project up on first use.

## 3. Code with any AI, then check

Open your project with any AI. It reads the rules file Selfproof created
(`CLAUDE.md`, `AGENTS.md` or `GEMINI.md`) and follows the same rules. When it is
done:

```bash
selfproof build
```

This checks whatever the AI wrote. Green means the rules held; a failure tells
you what to fix. The git hooks also run this automatically at commit and push.

That is it. More detail: [use with any AI](docs/guides/using-with-any-ai.md).
