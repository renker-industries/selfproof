from __future__ import annotations

import pytest

from renker_core.audit import AuditError, AuditLog


def _log(tmp_path):
    return AuditLog(tmp_path / "audit.log")


def _record(log, decision="ALLOW", outcome="success"):
    return log.record(
        actor="agent:a",
        action="filesystem.write",
        target="/tmp/x",
        capability="cap_1",
        policy_decision=decision,
        reason="test",
        outcome=outcome,
    )


def test_chain_links_and_verifies(tmp_path):
    log = _log(tmp_path)
    first = _record(log)
    second = _record(log)
    assert second.prev_hash == first.entry_hash
    log.verify()


def test_detects_modified_entry(tmp_path):
    log = _log(tmp_path)
    _record(log)
    _record(log)
    lines = log.log_path.read_text(encoding="utf-8").splitlines()
    lines[0] = lines[0].replace('"reason":"test"', '"reason":"forged"')
    log.log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    with pytest.raises(AuditError):
        log.verify()


def test_detects_tail_truncation(tmp_path):
    log = _log(tmp_path)
    _record(log)
    _record(log)
    lines = log.log_path.read_text(encoding="utf-8").splitlines()
    log.log_path.write_text(lines[0] + "\n", encoding="utf-8")
    with pytest.raises(AuditError):
        log.verify()


def test_detects_full_deletion(tmp_path):
    log = _log(tmp_path)
    _record(log)
    log.log_path.write_text("", encoding="utf-8")
    with pytest.raises(AuditError):
        log.verify()


def test_read_all_roundtrip(tmp_path):
    log = _log(tmp_path)
    _record(log, decision="DENY", outcome="blocked")
    events = log.read_all()
    assert len(events) == 1
    assert events[0].policy_decision == "DENY"
