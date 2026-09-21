# Contributing to renker-core

`renker-core` is the security-critical foundation of the Renker platform. Contributions follow a deliberately strict process.

## Ground rules

- **No code-comment style.** Code in this repo contains no inline comments, docstrings, JSDoc, or `TODO` markers. Understandability comes from clear naming. Documentation belongs in `README.md` files, ADRs, and the wiki.
- **Do not commit secrets.** No API keys, tokens, or `.env` files.
- **No force-push** to shared branches.
- **Tests and lint must be green** (`pytest`, `ruff check`) before merging.

## The Builder → Attacker → Reviewer cycle

For **security-relevant changes** — anything under `renker_core/permissions/`, `renker_core/capabilities/`, and `renker_core/crypto_interface/` — "Builder → done" is **not** enough. These changes always go through:

1. **Builder** — implements the feature with a clear Definition of Done.
2. **Attacker** — is explicitly tasked to **break** the feature (e.g. "bypass a capability boundary with a manipulated website payload"). This is not a normal code review but a targeted attack simulation.
3. **Reviewer** — evaluates the implementation and the attack results and decides on remediations.
4. **Test Generator** — derives permanent regression tests from the counterexample.
5. **Human Decision** — policy decisions (e.g. "What counts as critical risk?") stay with the human as the final authority.

For details, see `RENKER_VISION.md`, section 11.

## Crypto boundary

In `renker_core/crypto_interface/`, **only interfaces** are defined — never cryptographic implementations. See `renker_core/crypto_interface/README.md` and `SECURITY.md`.
