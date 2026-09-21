from __future__ import annotations

from datetime import datetime, timezone

from renker_core.audit import AuditLog
from renker_core.capabilities import Capability, CapabilityStore, PathScope
from renker_core.identity import Actor
from renker_core.integration import GuardedFilesystem
from renker_core.policy import Decision


def _setup(tmp_path):
    store = CapabilityStore()
    store.grant(
        Capability(
            capability="filesystem.write",
            scope=PathScope(base=str(tmp_path / "drafts")),
            granted_to="agent:a",
            granted_by="human:sebastian",
            issued_at=datetime.now(timezone.utc),
            expires_at=None,
        )
    )
    log = AuditLog(tmp_path / "audit.log")
    return GuardedFilesystem(store, log), log


def test_allowed_write_executes_and_audits(tmp_path):
    guard, log = _setup(tmp_path)
    target = tmp_path / "drafts" / "report.md"
    result = guard.write(Actor("agent", "a"), str(target), "hello")
    assert result.decision is Decision.ALLOW
    assert result.executed is True
    assert target.read_text(encoding="utf-8") == "hello"
    assert result.event.outcome == "success"
    log.verify()


def test_denied_write_does_not_execute(tmp_path):
    guard, log = _setup(tmp_path)
    target = tmp_path / "secret.txt"
    result = guard.write(Actor("agent", "a"), str(target), "oops")
    assert result.decision is Decision.DENY
    assert result.executed is False
    assert not target.exists()
    assert result.event.outcome == "blocked"
    log.verify()


def test_denied_read_of_unpermitted_action(tmp_path):
    guard, log = _setup(tmp_path)
    result = guard.read(Actor("agent", "a"), str(tmp_path / "drafts" / "report.md"))
    assert result.decision is Decision.DENY
    assert "filesystem.read" in result.reason
    log.verify()
