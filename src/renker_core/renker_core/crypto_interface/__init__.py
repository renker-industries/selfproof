from __future__ import annotations

from typing import Protocol, runtime_checkable

PRIMITIVE = "crypto_interface"


@runtime_checkable
class Encryptor(Protocol):
    def encrypt(self, plaintext: bytes, recipient: str) -> bytes: ...

    def decrypt(self, ciphertext: bytes, recipient: str) -> bytes: ...


@runtime_checkable
class Signer(Protocol):
    def sign(self, payload: bytes, key_id: str) -> bytes: ...


@runtime_checkable
class Verifier(Protocol):
    def verify(self, payload: bytes, signature: bytes, key_id: str) -> bool: ...


__all__ = ["PRIMITIVE", "Encryptor", "Signer", "Verifier"]
