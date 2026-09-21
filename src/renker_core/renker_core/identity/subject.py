from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from renker_core.identity.actor import Actor, IdentityError


@dataclass(frozen=True)
class Identity:
    kind: str
    identifier: str
    expires_at: datetime | None = None
    attributes: tuple[tuple[str, str], ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        Actor(kind=self.kind, identifier=self.identifier)
        if self.expires_at is not None and self.expires_at.tzinfo is None:
            raise IdentityError("identity expires_at must be timezone-aware or None")

    @property
    def urn(self) -> str:
        return f"{self.kind}:{self.identifier}"

    @property
    def actor(self) -> Actor:
        return Actor(kind=self.kind, identifier=self.identifier)

    def is_expired(self, now: datetime | None = None) -> bool:
        if self.expires_at is None:
            return False
        moment = now.astimezone(timezone.utc) if now is not None else datetime.now(timezone.utc)
        return moment >= self.expires_at.astimezone(timezone.utc)

    def attribute(self, key: str, default: str | None = None) -> str | None:
        for existing_key, value in self.attributes:
            if existing_key == key:
                return value
        return default

    @classmethod
    def from_actor(cls, actor: Actor) -> Identity:
        return cls(kind=actor.kind, identifier=actor.identifier)

    def __str__(self) -> str:
        return self.urn


__all__ = ["Identity"]
