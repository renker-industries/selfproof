from __future__ import annotations

from renker_core.capabilities.model import Capability


class CapabilityStore:
    def __init__(self) -> None:
        self._grants: dict[str, Capability] = {}
        self._revoked: set[str] = set()

    def grant(self, capability: Capability) -> str:
        self._grants[capability.capability_id] = capability
        return capability.capability_id

    def revoke(self, capability_id: str) -> bool:
        if capability_id not in self._grants:
            return False
        if not self._grants[capability_id].revocable:
            return False
        self._revoked.add(capability_id)
        return True

    def is_revoked(self, capability_id: str) -> bool:
        return capability_id in self._revoked

    def get(self, capability_id: str) -> Capability | None:
        return self._grants.get(capability_id)

    def find(self, actor_urn: str, action: str) -> list[Capability]:
        return [
            cap
            for cap in self._grants.values()
            if cap.granted_to == actor_urn and cap.capability == action
        ]
