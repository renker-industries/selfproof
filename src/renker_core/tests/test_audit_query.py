from __future__ import annotations

from datetime import datetime, timedelta, timezone

from renker_core.audit import AuditLog


def _log(tmp_path):
    log = AuditLog(tmp_path / "audit.log")
    log.record(
        actor="agent:a",
        action="filesystem.write",
        target="/x",
        capability="cap_a",
        policy_decision="ALLOW",
        reason="ok",
        outcome="success",
    )
    log.record(
        actor="agent:b",
        action="filesystem.read",
        target="/y",
        capability="cap_b",
        policy_decision="DENY",
        reason="scope",
        outcome="blocked",
    )
    log.record(
        actor="agent:a",
        action="filesystem.write",
        target="/z",
        capability="cap_a",
        policy_decision="DENY",
        reason="revoked",
        outcome="blocked",
    )
    return log


def test_filter_by_actor(tmp_path):
    log = _log(tmp_path)
    assert len(log.query(actor="agent:a")) == 2
    assert len(log.query(actor="agent:b")) == 1


def test_filter_by_decision_and_outcome(tmp_path):
    log = _log(tmp_path)
    assert len(log.query(decision="DENY")) == 2
    assert len(log.query(outcome="success")) == 1


def test_filter_by_action_and_capability(tmp_path):
    log = _log(tmp_path)
    assert len(log.query(action="filesystem.read")) == 1
    assert len(log.query(capability="cap_a")) == 2


def test_combined_filters(tmp_path):
    log = _log(tmp_path)
    assert len(log.query(actor="agent:a", decision="DENY")) == 1


def test_time_range(tmp_path):
    log = _log(tmp_path)
    now = datetime.now(timezone.utc)
    assert len(log.query(since=now - timedelta(hours=1))) == 3
    assert len(log.query(until=now - timedelta(hours=1))) == 0


def test_query_does_not_mutate_source(tmp_path):
    log = _log(tmp_path)
    before = log.log_path.read_text(encoding="utf-8")
    log.query(actor="agent:a")
    after = log.log_path.read_text(encoding="utf-8")
    assert before == after
    log.verify()
