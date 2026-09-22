from __future__ import annotations

from datetime import datetime, timedelta, timezone


def _now(now: datetime | None) -> datetime:
    return now if now is not None else datetime.now(timezone.utc)


class ReplayGuard:
    def __init__(self, ttl_seconds: int = 300, clock_skew_seconds: int = 60) -> None:
        self._ttl = ttl_seconds
        self._skew = clock_skew_seconds
        self._seen: dict[str, datetime] = {}

    def check(self, *, nonce: str, issued_at: datetime, now: datetime | None = None) -> bool:
        moment = _now(now)
        if issued_at.tzinfo is None:
            return False
        issued = issued_at.astimezone(timezone.utc)
        if issued > moment + timedelta(seconds=self._skew):
            return False
        if (moment - issued).total_seconds() > self._ttl:
            return False
        self._prune(moment)
        if not nonce or nonce in self._seen:
            return False
        self._seen[nonce] = moment + timedelta(seconds=self._ttl)
        return True

    def _prune(self, moment: datetime) -> None:
        expired = [nonce for nonce, deadline in self._seen.items() if deadline <= moment]
        for nonce in expired:
            del self._seen[nonce]


__all__ = ["ReplayGuard"]
