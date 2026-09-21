from __future__ import annotations

from dataclasses import dataclass

from renker_core.model import Action, Resource, ResourcePattern

PRIMITIVE = "permissions"

APPROVAL_POLICIES = ("auto", "deny", "human")


@dataclass(frozen=True)
class Permission:
    action: Action
    resource: ResourcePattern

    def permits(self, action: Action, resource: Resource) -> bool:
        return self.action == action and self.resource.matches(resource)

    def describe(self) -> str:
        return f"{self.action.dotted} on {self.resource.describe()}"


__all__ = ["PRIMITIVE", "APPROVAL_POLICIES", "Permission"]
