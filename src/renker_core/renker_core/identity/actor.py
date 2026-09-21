from __future__ import annotations

from dataclasses import dataclass

ACTOR_KINDS = ("human", "agent", "device", "service")


class IdentityError(ValueError):
    pass


@dataclass(frozen=True)
class Actor:
    kind: str
    identifier: str

    def __post_init__(self) -> None:
        if self.kind not in ACTOR_KINDS:
            raise IdentityError(f"unknown actor kind: {self.kind!r}")
        ident = self.identifier
        if not isinstance(ident, str) or not ident or ident.strip() != ident:
            raise IdentityError("actor identifier must be a non-empty, untrimmed string")
        if any(char.isspace() for char in ident) or not ident.isprintable():
            raise IdentityError("actor identifier has control or whitespace characters")
        if ":" in ident or "/" in ident or "\\" in ident:
            raise IdentityError(f"actor identifier contains forbidden characters: {ident!r}")

    @property
    def urn(self) -> str:
        return f"{self.kind}:{self.identifier}"

    @classmethod
    def from_urn(cls, urn: str) -> Actor:
        if urn.count(":") != 1:
            raise IdentityError(f"malformed actor urn: {urn!r}")
        kind, identifier = urn.split(":", 1)
        return cls(kind=kind, identifier=identifier)

    def __str__(self) -> str:
        return self.urn
