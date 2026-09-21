from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

APPROVAL_POLICIES = ("auto", "deny", "human")
RISK_TIERS = ("low", "medium", "high", "critical")


class CapabilityError(ValueError):
    pass


@dataclass(frozen=True)
class PathScope:
    base: str

    def __post_init__(self) -> None:
        if not isinstance(self.base, str) or not self.base.strip():
            raise CapabilityError("path scope base must be a non-empty string")

    def _resolved_base(self) -> Path:
        return Path(self.base).expanduser().resolve()

    def permits(self, target: str) -> bool:
        if not isinstance(target, str) or not target:
            return False
        try:
            resolved_target = Path(target).expanduser().resolve()
        except (OSError, RuntimeError, ValueError):
            return False
        base = self._resolved_base()
        if resolved_target == base:
            return True
        return _is_within(resolved_target, base)

    def describe(self) -> str:
        return f"{self._resolved_base()}{_os_sep()}**"


def _os_sep() -> str:
    return "\\" if "\\" in str(Path("a") / "b") else "/"


def _normcased_parts(path: Path) -> tuple[str, ...]:
    return tuple(os.path.normcase(part) for part in path.parts)


def _is_within(target: Path, base: Path) -> bool:
    base_parts = _normcased_parts(base)
    target_parts = _normcased_parts(target)
    if len(target_parts) <= len(base_parts):
        return False
    return target_parts[: len(base_parts)] == base_parts


@dataclass(frozen=True)
class Capability:
    capability: str
    scope: PathScope
    granted_to: str
    granted_by: str
    issued_at: datetime
    expires_at: datetime | None
    approval_policy: str = "auto"
    risk_tier: str = "low"
    revocable: bool = True
    audit_required: bool = True
    capability_id: str = field(default="")

    def __post_init__(self) -> None:
        if not self.capability or "." not in self.capability:
            raise CapabilityError(f"capability must be a dotted verb, got {self.capability!r}")
        if self.approval_policy not in APPROVAL_POLICIES:
            raise CapabilityError(f"unknown approval_policy: {self.approval_policy!r}")
        if self.risk_tier not in RISK_TIERS:
            raise CapabilityError(f"unknown risk_tier: {self.risk_tier!r}")
        if _as_utc(self.issued_at) is None:
            raise CapabilityError("issued_at must be timezone-aware")
        if self.expires_at is not None and _as_utc(self.expires_at) is None:
            raise CapabilityError("expires_at must be timezone-aware or None")
        if not self.capability_id:
            object.__setattr__(self, "capability_id", self._derive_id())

    def _derive_id(self) -> str:
        material = "|".join(
            [
                self.capability,
                self.scope.base,
                self.granted_to,
                self.granted_by,
                self.issued_at.isoformat(),
                self.expires_at.isoformat() if self.expires_at else "none",
            ]
        )
        digest = hashlib.sha256(material.encode("utf-8")).hexdigest()
        return f"cap_{digest[:16]}"

    def is_expired(self, now: datetime | None = None) -> bool:
        if self.expires_at is None:
            return False
        moment = now.astimezone(timezone.utc) if now is not None else datetime.now(timezone.utc)
        return moment >= self.expires_at.astimezone(timezone.utc)

    def permits_action(self, action: str) -> bool:
        return action == self.capability

    def permits_target(self, target: str) -> bool:
        return self.scope.permits(target)


def _as_utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return None
    return value.astimezone(timezone.utc)
