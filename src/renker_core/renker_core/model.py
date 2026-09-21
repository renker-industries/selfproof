from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


class ModelError(ValueError):
    pass


def _reject_bad_token(value: str, label: str) -> None:
    if not isinstance(value, str) or not value or value.strip() != value:
        raise ModelError(f"{label} must be a non-empty, untrimmed string")
    if any(char.isspace() for char in value) or not value.isprintable():
        raise ModelError(f"{label} must not contain whitespace or control characters")


@dataclass(frozen=True)
class Action:
    namespace: str
    verb: str

    def __post_init__(self) -> None:
        for value, label in ((self.namespace, "action namespace"), (self.verb, "action verb")):
            _reject_bad_token(value, label)
            if "." in value or ":" in value:
                raise ModelError(f"{label} must not contain '.' or ':'")

    @property
    def dotted(self) -> str:
        return f"{self.namespace}.{self.verb}"

    @classmethod
    def parse(cls, dotted: str) -> Action:
        if not isinstance(dotted, str) or dotted.count(".") != 1:
            raise ModelError(f"action must be 'namespace.verb', got {dotted!r}")
        namespace, verb = dotted.split(".", 1)
        return cls(namespace=namespace, verb=verb)

    def __str__(self) -> str:
        return self.dotted


@dataclass(frozen=True)
class Resource:
    type: str
    identifier: str

    def __post_init__(self) -> None:
        _reject_bad_token(self.type, "resource type")
        if not isinstance(self.identifier, str) or not self.identifier:
            raise ModelError("resource identifier must be a non-empty string")

    @property
    def urn(self) -> str:
        return f"{self.type}:{self.identifier}"

    def __str__(self) -> str:
        return self.urn


def _normcased_parts(path: Path) -> tuple[str, ...]:
    return tuple(os.path.normcase(part) for part in path.parts)


@dataclass(frozen=True)
class ResourcePattern:
    base: str

    def __post_init__(self) -> None:
        if not isinstance(self.base, str) or not self.base.strip():
            raise ModelError("resource pattern base must be a non-empty string")

    def _resolved_base(self) -> Path:
        return Path(self.base).expanduser().resolve()

    def matches(self, resource: Resource) -> bool:
        return self.matches_identifier(resource.identifier)

    def matches_identifier(self, identifier: str) -> bool:
        if not isinstance(identifier, str) or not identifier:
            return False
        try:
            target = Path(identifier).expanduser().resolve()
        except (OSError, RuntimeError, ValueError):
            return False
        base = self._resolved_base()
        if target == base:
            return True
        base_parts = _normcased_parts(base)
        target_parts = _normcased_parts(target)
        if len(target_parts) <= len(base_parts):
            return False
        return target_parts[: len(base_parts)] == base_parts

    def describe(self) -> str:
        return f"{self._resolved_base()}{os.sep}**"


ENVIRONMENTS = ("production", "staging", "development", "unknown")


@dataclass(frozen=True)
class Context:
    environment: str = "unknown"
    user_present: bool = False
    network: str = "unknown"
    attributes: tuple[tuple[str, str], ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.environment not in ENVIRONMENTS:
            raise ModelError(f"unknown environment: {self.environment!r}")

    def attribute(self, key: str, default: str | None = None) -> str | None:
        for existing_key, value in self.attributes:
            if existing_key == key:
                return value
        return default


__all__ = [
    "ModelError",
    "Action",
    "Resource",
    "ResourcePattern",
    "Context",
    "ENVIRONMENTS",
]
