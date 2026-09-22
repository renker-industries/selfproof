# Owner to-do

Open questions and manual steps that only the owner can do. Each has a
recommended default; work that does not depend on it continues.

## Gated irreversible actions (need a live owner OK)
- [ ] **A3 — relicense `renker-core` to Apache-2.0.** Recommended. Requires first
  checking the `renker-core` git history for outside contributors. This is a
  legal change and is executed only on explicit confirmation, then imported
  changes follow. Default if unanswered: keep the kernel proprietary (its own
  LICENSE governs `src/renker_core/`), repo stays private.
- [ ] **A4 — make the repository public.** Only after the release-readiness check
  (Phase 8) passes. Default: stay private.

## Manual steps (cannot be scripted)
- [ ] **Commit signing.** No signing key is configured (`signing: none`).
  Set `git config user.signingkey` and `gpg.format`, then "require signed
  commits" can be enabled. Needed for protected-path approvals.
- [ ] **Fine-grained token.** The active `gh` token is a **classic** token with
  full `repo` scope (`gist, read:org, repo, workflow`) — it can touch every repo,
  not just the two in scope. Recommended: create a fine-grained token limited to
  `renker-industries/selfproof` and `-holdout`. Residual risk until then: broad
  write access. (Can only be done in the GitHub web UI.)
- [ ] **Branch protection / ruleset — BLOCKED by plan.** Both branch protection
  and repository rulesets return HTTP 403 "Upgrade to GitHub Pro or make this
  repository public" for this private repo. Until the repo is public (A4) or the
  account is on Pro/Team, `main` cannot be protected server-side; enforcement
  relies on the local git hooks + a red CI run. Applied intent (to set once
  available): require the `gates` check, require PRs, linear history, block
  force-push/deletion, no admin bypass, 0 required approvals (solo-maintainer).
- [ ] **Secret scanning — BLOCKED by plan.** HTTP 422 "not available for this
  repository" (needs GitHub Advanced Security / public). Dependabot alerts and
  automated security fixes ARE enabled. Enable code scanning and secret scanning
  when the plan allows or on publication.
- [ ] **Passkey/2FA** on both accounts and minimal org member permissions.
- [ ] **First wiki page.** GitHub creates `<repo>.wiki.git` only after the first
  page is created in the web UI (Phase 6).
- [ ] **Archive the autopilot prompt source.** Add the owner's byte-exact prompt
  file to `docs/prompts/` and record its SHA-256 (see `docs/prompts/README.md`).

## Open decisions (concept 16.3)
- [ ] Confirm the name **Selfproof** after checks (registry checks passed
  2026-09-21; trademark search still pending — see ADR-0001).
- [ ] Which Tier B classes, if any, to pre-approve (default: none).
- [ ] Archive the old repos after migration (charter A5 = NO).
- [ ] Agent order for adapters (default: Claude Code, Codex, then the rest).

## Release follow-ups (for publication / full v0.1.0)
- [ ] **Populate the holdout** (`renker-industries/selfproof-holdout`) from a
  session that is not the builder, so improvement cycles resist overfitting. The
  builder must never read these cases. Until then, Phase 9's "≥3 proven cycles on
  the holdout" is pending.
- [ ] **Install the external scanners in CI** (gitleaks, osv-scanner, zizmor) so
  the `security` gate runs them for real, and run a full-history secret scan
  before any publication.

## Hardening follow-ups
- [ ] Pin GitHub Actions by full commit SHA (currently tag-pinned in `ci.yml`).
  Note: `zizmor` will flag unpinned actions, so do this before wiring zizmor into
  CI.
