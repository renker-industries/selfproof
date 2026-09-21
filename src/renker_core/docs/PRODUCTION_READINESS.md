# Production Readiness — Renker repositories

- **Date:** 2026-08-12
- **Honest verdict up front:** this pass **hardened** the repos toward the strictest widely-recognized bars.
  It does **not** declare them "certified production-ready" — that requires an external audit, code-signing
  certificates, and (for `renkervault`/`continuum`) deeper review than was in scope. Every claim below is
  either *done and verified* or listed as an open gap.

## The rubric (strictest recognized standards)
- **OpenSSF Best Practices Badge** (passing → silver → gold) and **OpenSSF Scorecard** checks: pinned
  dependencies, branch protection, CI tests, code review, token permissions, SAST, signed releases.
- **SLSA** (Supply-chain Levels for Software Artifacts): build provenance, ideally L2–L3.
- **NIST SSDF (SP 800-218)**: secure development practices.
- **Installer/distribution:** checksummed **and** code-signed artifacts; reproducibility where feasible.

## What was hardened this pass (done + verified)
- **CI pipelines pinned to commit SHAs** (Scorecard: Pinned-Dependencies) for `renker-core` and
  `renker-core-authz`, with least-privilege `permissions: contents: read` and `concurrency`.
- **Signed-ready, checksummed releases:** new `Release` workflow on both — builds sdist+wheel, emits
  `SHA256SUMS.txt`, and produces a **SLSA build-provenance attestation** (`actions/attest-build-provenance`),
  gated on the full quality suite + a tag/version match check.
- **Project hygiene:** `SECURITY.md`, `CONTRIBUTING.md`, `CODEOWNERS`, `dependabot.yml` (pip + actions),
  `CHANGELOG.md` added where missing.
- **Installer verifiability:** `SHA256SUMS.txt` attached to the live rencora `v21.1` installer release
  (`RENCORA_Setup.exe` → `85cde6a9…`), plus an additive workflow that auto-checksums every future rencora
  release.

## Per-repo scorecard

| Repo | Tests/Types/Lint | CI pinned + least-priv | Signed/checksummed release | Hygiene | Verdict |
|---|---|---|---|---|---|
| **renker-core** | ✅ 132, mypy, ruff, pip-audit | ✅ this pass | ⚠️ checksums+SLSA ready; **not code-signed** | ✅ | Strong; not externally audited |
| **renker-core-authz** | ✅ 89, mypy, ruff, pip-audit | ✅ this pass | ⚠️ checksums+SLSA ready; **no PyPI publish yet** | ✅ | Strong; the shipped core |
| **rencora** | app; black-box EXE-verified | ⚠️ `build.yml` unchanged (yours) | ⚠️ **checksums now ✅**, **code-signing pending cert** | ⚠️ partial | Installer verifiable, not signed |
| **renkervault** | has `security-ci`, dependabot | audit-only | ✅ release has SHA256SUMS + NSIS/MSI | ⚠️ missing CONTRIBUTING/CODEOWNERS | Good hygiene; **not deep-reviewed here** |
| **continuum** | has `ci.yml` (MIT) | audit-only | none | ✗ missing SECURITY/dependabot/etc. | Phase-0 prototype; **not production** |

## Open gaps — require **you** (cannot be done from here honestly)
1. **Code-signing certificate (Authenticode).** Without it the Windows installer cannot be truly signed.
   Once you provide a cert (as GitHub secrets), the rencora release can `signtool sign` the `.exe` and the
   installers become production-signed. Until then: verifiable via `SHA256SUMS.txt`, **not** signed.
2. **Branch protection** on `main`/`master` (required reviews, required CI, no force-push). I can enable this
   via API on the repos you own if you say go.
3. **External security audit** — by definition external; a passing internal adversarial suite is not a
   substitute.
4. **renkervault / continuum deep hardening** — deliberately **audit-only** this pass to avoid breaking code
   I have not fully reviewed. Recommended next: add their missing hygiene files and run their suites before
   any code changes.

## How to verify what shipped
```bash
# rencora installer
gh release download v21.1 --repo sebastianrenker/rencora
sha256sum -c SHA256SUMS.txt        # must print: RENCORA_Setup.exe: OK

# a future library release (after tagging vX.Y.Z)
gh attestation verify dist/renker_core-*.whl --repo sebastianrenker/renker-core
```
