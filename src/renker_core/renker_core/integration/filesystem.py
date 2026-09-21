from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from renker_core.audit.log import AuditEvent, AuditLog
from renker_core.capabilities.store import CapabilityStore
from renker_core.identity.actor import Actor
from renker_core.policy.engine import Decision, PolicyResult, evaluate

READ = "filesystem.read"
WRITE = "filesystem.write"


@dataclass(frozen=True)
class GuardResult:
    decision: Decision
    reason: str
    event: AuditEvent
    value: str | None = None
    executed: bool = False


class GuardedFilesystem:
    def __init__(self, store: CapabilityStore, audit_log: AuditLog) -> None:
        self._store = store
        self._audit = audit_log

    def read(self, actor: Actor, target: str) -> GuardResult:
        return self._guard(READ, actor, target, self._do_read)

    def write(self, actor: Actor, target: str, content: str) -> GuardResult:
        def run(path: Path) -> str:
            return self._do_write(path, content)

        return self._guard(WRITE, actor, target, run)

    def _guard(
        self,
        action: str,
        actor: Actor,
        target: str,
        execute: Callable[[Path], str],
    ) -> GuardResult:
        result: PolicyResult = evaluate(
            actor=actor, action=action, target=target, store=self._store
        )

        if result.decision is not Decision.ALLOW:
            event = self._record(result, outcome="blocked")
            return GuardResult(
                decision=result.decision,
                reason=result.reason,
                event=event,
                executed=False,
            )

        try:
            value = execute(Path(target).expanduser())
        except OSError as error:
            event = self._record(result, outcome="error")
            return GuardResult(
                decision=result.decision,
                reason=f"{result.reason}; execution failed: {error}",
                event=event,
                executed=False,
            )

        event = self._record(result, outcome="success")
        return GuardResult(
            decision=result.decision,
            reason=result.reason,
            event=event,
            value=value,
            executed=True,
        )

    def _record(self, result: PolicyResult, outcome: str) -> AuditEvent:
        return self._audit.record(
            actor=result.actor,
            action=result.action,
            target=result.target,
            capability=result.capability_id,
            policy_decision=result.decision.value,
            reason=result.reason,
            outcome=outcome,
        )

    @staticmethod
    def _do_read(path: Path) -> str:
        return path.read_text(encoding="utf-8")

    @staticmethod
    def _do_write(path: Path, content: str) -> str:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return str(path)
