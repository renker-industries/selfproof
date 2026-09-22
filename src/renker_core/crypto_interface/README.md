# crypto_interface

**Primitive:** Crypto boundary (part of Security)

**Purpose:** Defines **only interfaces and types** for cryptographic operations (`Encryptor`, `Signer`, `Verifier`) — e.g. "encrypt this payload for this recipient" or "verify this signature". **No** cryptographic implementation is placed here.

> ⚠️ **Important security note — do not implement your own cryptography.**
> The actual crypto implementation belongs in a separate, minimal, strictly audited module (ideally under RenkerVault or its own `renker-crypto` repo), built on established, vetted primitives such as **libsodium/NaCl** or Signal-protocol building blocks — never as an in-house design. Separating interface from implementation keeps the attack surface small and makes external audits realistic (see Vision, section 4.3).

**Used by:** primarily RenkerVault; the interfaces are usable across products.

> Security-relevant module. Changes here go through the Builder→Attacker→Reviewer cycle from `CONTRIBUTING.md`.

**Note on structure:** The Vision (section 4.1) notes this folder as `crypto-interface/`. Since Python import paths do not allow a hyphen and the requirement is "runnably importable", it is implemented here as `crypto_interface/`.
