# Changelog

All notable changes to this project are documented here, following
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- Seed of the platform (Phase 1): repository, Apache-2.0 license and NOTICE,
  SECURITY policy, autonomy charter, and the concept under `docs/`.
- Imported `renker-core` kernel with full history into `src/renker_core/`
  (132 kernel tests green, unchanged).
- Evidence ledger built on the kernel audit chain (`selfproof.core.ledger`).
- Gate runner and the `language` and `proof` gates, each with a corpus.
- `selfproof` CLI: `status`, `build`, `ledger verify`, `autopilot`.
- CI workflow (verify-only, read-only token) and documentation skeleton
  (ADR-0001 name, ADR-0002 inventory, ADR-0003 scouting, gate references).
- Cutover to the self-hosted stage (`self-host-v0`): CI ran the platform on a
  deliberately-bad PR and the language gate blocked it; stage set to
  `self-hosted` via `selfproof.toml`.
- Private holdout repository `renker-industries/selfproof-holdout` (A9) with the
  anti-gaming contract.
- Phase 2 gates (batch A): `slop` (AST/text heuristics), `architecture`
  (layering, cycles, size budgets, dependency ADRs) and `test_weakening`
  (diff-based), each with a corpus/tests and a gate reference.
- Phase 2 gates (batch B): `docs_coverage` (docstrings, per-directory READMEs,
  gate references, CLI reference) and `docs_claims` (no absolute claims,
  labelled numbers), plus `scripts/gen_cli_reference.py` and the generated
  `docs/reference/cli.md`. All seven gates pass on the repo.
- Phase 2 gate (batch C): `security` — built-in secret scan, license check and
  workflow hardening check, augmented by gitleaks/osv-scanner/zizmor when
  installed. All eight gates now exist (`security` reports SKIPPED until the
  external scanners are installed — a missing tool is never a pass).
- Phase 3 (adapters): the adapter registry with honest capability levels
  (`git` L1, `claude_code`/`codex`/`gemini_cli`/`cursor`/`aider` L1, `ollama`
  L0). No L2 is claimed yet (no native session hook is wired). Adds
  `scripts/gen_capability_matrix.py` and the generated capability matrix.
- Phase 3 (rules format): `rules/agents.yaml` is the single source; `CLAUDE.md`,
  `AGENTS.md` and `GEMINI.md` are generated from it (`scripts/gen_agent_rules.py`,
  `selfproof rules generate`). `selfproof rules check` fails on drift and runs in
  CI, so a stale or hand-edited generated file is caught.
- Phase 4 (token module): `selfproof.tokens` measures the net token saving
  (`baseline - actual - overhead`) from paired benchmark runs, with
  `selfproof bench report`. No number is invented: percentages come only from
  benchmark files, unmeasured runs are never counted as zero, and below n=5 the
  report shows `insufficient data`. No real runs are recorded yet.
- Phase 5 (dashboard): `selfproof.dashboard` reads the ledger, git and the
  benchmarks and renders a self-contained (no-CDN), dark, accessible HTML export
  and a terminal summary. `selfproof dashboard show` / `dashboard export --out`.
  A test guarantees the export leaks no file paths, usernames or raw ledger
  hashes.
- Dashboard redesign: a crafted single-file UI — restrained dark theme with a
  light-mode fallback, clear type hierarchy, tabular numerals, inline-SVG gate
  bars, and an embedded web app manifest so it installs via "Add to Home Screen"
  on phones and desktops (no service worker, so it stays script-free). New
  `selfproof dashboard open` builds and opens it in the default browser
  (Windows/macOS/Linux).
