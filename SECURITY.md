# Security Policy

## Reporting a vulnerability

Report suspected vulnerabilities privately through GitHub's private
vulnerability reporting on this repository, or by email to
**sebastian.renker3@gmail.com**. Please do not open a public issue for a
security problem.

We aim to acknowledge a report within 7 days. There is no bug-bounty program.

## What Selfproof does and does not promise

Selfproof records evidence for every check it runs and binds each result to an
exact commit. It does **not** promise that any code is "absolutely secure",
"unhackable" or "bug-free" — no program can prove that.

The strongest statement Selfproof makes is of the form:

> 0 known findings at commit `<sha>` according to `<tools and versions>` on `<date>`.

## Known limitations of the security model

- **Solo-maintainer human gate.** Branch protection cannot require a second
  reviewer when there is only one maintainer. Protected-path changes are gated
  instead by a signed approval commit verified in CI against a pinned
  `allowed_signers` file. This is a weaker control than an independent reviewer
  and is stated here on purpose.
- **Ledger truncation.** The evidence ledger is a hash chain. A hash chain
  detects edited entries but not a truncated tail. The chain head is therefore
  anchored in every signed release tag and release note so truncation is
  detectable against the last release.
- **Actor authentication.** The kernel does not yet cryptographically
  authenticate actors. Until signed identities exist, the git commit signature
  carries that trust.
- **Secret rotation is manual.** If a scan finds a secret, rotation at the
  provider is a manual step for the owner; Selfproof never handles credentials.

## Supported versions

This project is pre-release (bootstrapping). No version is supported for
production use yet.
