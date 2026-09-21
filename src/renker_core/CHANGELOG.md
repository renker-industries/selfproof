# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Hardened CI: GitHub Actions pinned by commit SHA, least-privilege `permissions`, `concurrency`.
- `Release` workflow: sdist + wheel, `SHA256SUMS.txt`, SLSA build-provenance attestation, GitHub Release on
  `v*` tags, gated on the full quality suite and a tag/version match check.
- Project hygiene: `CODEOWNERS`, `dependabot.yml`, this changelog.

## [0.2.0] - 2026-08-11
### Changed
- **Breaking:** the public `Decision` is now the rich, immutable, serializable decision record; the effect
  enum is `Effect` (`policy.Decision` remains an alias for backward compatibility). See ADR 0006.
### Added
- Security decision kernel: strong types (`Action`/`Resource`/`ResourcePattern`/`Context`), `Identity`,
  `Permission`, versioned `Policy`/`Rule`, `PolicyEngine` protocol + `StaticPolicyEngine`, fail-closed
  `Authorizer`, real `Approval` model + `ReplayGuard`, `RiskAssessment`, and an `AuditSink` layer with a
  decision-linked, tamper-evident hash chain. 132 tests.

## [0.1.0] - 2026-08-10
### Added
- Foundation slice: identity, capabilities, deterministic policy, tamper-evident audit, guarded filesystem;
  frozen public API, CI quality gate, threat model, and the extracted public package `renker-core-authz`.
