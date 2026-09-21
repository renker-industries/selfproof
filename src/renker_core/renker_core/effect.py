from __future__ import annotations

from enum import Enum


class Effect(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"


__all__ = ["Effect"]
