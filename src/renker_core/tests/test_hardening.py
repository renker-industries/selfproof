from __future__ import annotations

import os
import threading
from datetime import datetime, timedelta, timezone

import pytest

from renker_core.audit import AuditError, AuditLog
from renker_core.capabilities import Capability, CapabilityError, CapabilityStore, PathScope
from renker_core.identity import Actor, IdentityError
from renker_core.integration import GuardedFilesystem
from renker_core.policy import Decision, evaluate


def _cap(tmp_path, **overrides):
    base = dict(
        capability="filesystem.write",
        scope=PathScope(base=str(tmp_path / "drafts")),
        granted_to="agent:a",
        granted_by="human:sebastian",
        issued_at=datetime.now(timezone.utc),
        expires_at=None,
    )
    base.update(overrides)
    return Capability(**base)


def _store(cap):
    store = CapabilityStore()
    store.grant(cap)
    return store


def _decision(store, target, actor="agent:a", action="filesystem.write"):
    return evaluate(
        actor=Actor.from_urn(actor),
        action=action,
        target=str(target),
        store=store,
    ).decision


class TestScopeHardening:
    def test_empty_base_rejected(self):
        with pytest.raises(CapabilityError):
            PathScope(base="")

    def test_whitespace_base_rejected(self):
        with pytest.raises(CapabilityError):
            PathScope(base="   ")

    def test_permits_rejects_empty_target(self, tmp_path):
        assert PathScope(base=str(tmp_path)).permits("") is False

    @pytest.mark.skipif(os.name != "nt", reason="Windows is case-insensitive")
    def test_windows_case_insensitive_same_dir_allowed(self, tmp_path):
        scope = PathScope(base=str(tmp_path / "Documents"))
        assert scope.permits(str(tmp_path / "documents" / "x.txt")) is True

    def test_prefix_confusion_still_blocked_after_normcase(self, tmp_path):
        scope = PathScope(base=str(tmp_path / "Documents"))
        assert scope.permits(str(tmp_path / "Documents2" / "x.txt")) is False

    def test_double_dot_stacked_traversal(self, tmp_path):
        scope = PathScope(base=str(tmp_path / "a" / "b" / "c"))
        assert scope.permits(str(tmp_path / "a" / "b" / "c" / ".." / ".." / "secret")) is False

    def test_base_itself_is_permitted(self, tmp_path):
        base = tmp_path / "drafts"
        assert PathScope(base=str(base)).permits(str(base)) is True


class TestIdentityHardening:
    @pytest.mark.parametrize("bad", ["a\x00b", "a\nb", "a\tb", "a\x1bb"])
    def test_control_characters_rejected(self, bad):
        with pytest.raises(IdentityError):
            Actor("agent", bad)

    def test_unicode_identifier_allowed(self):
        actor = Actor("agent", "sitzung-ärztin-42")
        assert actor.urn == "agent:sitzung-ärztin-42"

    def test_non_string_identifier_rejected(self):
        with pytest.raises(IdentityError):
            Actor("agent", 123)  # type: ignore[arg-type]


class TestPolicyHardening:
    def test_expiry_exact_boundary_denies(self, tmp_path):
        now = datetime(2026, 1, 1, tzinfo=timezone.utc)
        cap = _cap(tmp_path, issued_at=now - timedelta(hours=1), expires_at=now)
        result = evaluate(
            actor=Actor("agent", "a"),
            action="filesystem.write",
            target=str(tmp_path / "drafts" / "x"),
            store=_store(cap),
            now=now,
        )
        assert result.decision is Decision.DENY

    def test_human_kind_with_same_identifier_is_distinct(self, tmp_path):
        cap = _cap(tmp_path, granted_to="agent:a")
        assert _decision(_store(cap), tmp_path / "drafts" / "x", actor="human:a") is Decision.DENY

    def test_overlapping_grants_expired_and_valid_allows(self, tmp_path):
        now = datetime.now(timezone.utc)
        expired = _cap(
            tmp_path, issued_at=now - timedelta(hours=2), expires_at=now - timedelta(hours=1)
        )
        valid = _cap(tmp_path, issued_at=now, expires_at=now + timedelta(hours=1))
        store = CapabilityStore()
        store.grant(expired)
        store.grant(valid)
        assert _decision(store, tmp_path / "drafts" / "x") is Decision.ALLOW

    def test_action_case_mismatch_denied(self, tmp_path):
        cap = _cap(tmp_path)
        decision = _decision(_store(cap), tmp_path / "drafts" / "x", action="Filesystem.Write")
        assert decision is Decision.DENY

    def test_empty_action_denied(self, tmp_path):
        cap = _cap(tmp_path)
        assert _decision(_store(cap), tmp_path / "drafts" / "x", action="") is Decision.DENY

    def test_none_action_denied_without_crash(self, tmp_path):
        cap = _cap(tmp_path)
        result = evaluate(
            actor=Actor("agent", "a"),
            action=None,  # type: ignore[arg-type]
            target=str(tmp_path / "drafts" / "x"),
            store=_store(cap),
        )
        assert result.decision is Decision.DENY

    def test_revoke_then_regrant_new_id_allows(self, tmp_path):
        store = CapabilityStore()
        cap = _cap(tmp_path)
        cid = store.grant(cap)
        store.revoke(cid)
        assert _decision(store, tmp_path / "drafts" / "x") is Decision.DENY
        fresh = _cap(tmp_path, issued_at=datetime.now(timezone.utc) + timedelta(seconds=1))
        store.grant(fresh)
        assert _decision(store, tmp_path / "drafts" / "x") is Decision.ALLOW


class TestAuditHardening:
    def _log(self, tmp_path):
        return AuditLog(tmp_path / "audit.log")

    def test_concurrent_appends_keep_chain_valid(self, tmp_path):
        log = self._log(tmp_path)

        def worker(n):
            for _ in range(n):
                log.record(
                    actor="agent:a",
                    action="filesystem.write",
                    target="/x",
                    capability="cap",
                    policy_decision="ALLOW",
                    reason="r",
                    outcome="success",
                )

        threads = [threading.Thread(target=worker, args=(50,)) for _ in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        events = log.read_all()
        assert len(events) == 400
        log.verify()

    def test_corrupt_line_raises_audit_error(self, tmp_path):
        log = self._log(tmp_path)
        log.record(
            actor="a",
            action="x",
            target="t",
            capability=None,
            policy_decision="ALLOW",
            reason="r",
            outcome="success",
        )
        with open(log.log_path, "a", encoding="utf-8") as handle:
            handle.write("{not valid json\n")
        with pytest.raises(AuditError):
            log.read_all()

    def test_reordering_detected(self, tmp_path):
        log = self._log(tmp_path)
        for _ in range(3):
            log.record(
                actor="a",
                action="x",
                target="t",
                capability=None,
                policy_decision="ALLOW",
                reason="r",
                outcome="success",
            )
        lines = log.log_path.read_text(encoding="utf-8").splitlines()
        lines[0], lines[1] = lines[1], lines[0]
        log.log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        with pytest.raises(AuditError):
            log.verify()

    def test_verify_empty_log_ok(self, tmp_path):
        self._log(tmp_path).verify()


class TestIntegrationHardening:
    def _guard(self, tmp_path):
        store = _store(_cap(tmp_path))
        return GuardedFilesystem(store, AuditLog(tmp_path / "audit.log"))

    def test_write_then_read_denied_without_read_capability(self, tmp_path):
        guard = self._guard(tmp_path)
        w = guard.write(Actor("agent", "a"), str(tmp_path / "drafts" / "f.txt"), "data")
        assert w.executed is True
        r = guard.read(Actor("agent", "a"), str(tmp_path / "drafts" / "f.txt"))
        assert r.decision is Decision.DENY

    def test_denied_action_never_touches_disk(self, tmp_path):
        guard = self._guard(tmp_path)
        target = tmp_path / "outside" / "f.txt"
        guard.write(Actor("agent", "a"), str(target), "data")
        assert not target.exists()

    def test_allowed_but_unwritable_parent_is_audited_as_error(self, tmp_path):
        store = _store(_cap(tmp_path, scope=PathScope(base=str(tmp_path / "drafts"))))
        guard = GuardedFilesystem(store, AuditLog(tmp_path / "audit.log"))
        blocker = tmp_path / "drafts"
        blocker.write_text("i am a file, not a dir", encoding="utf-8")
        result = guard.write(Actor("agent", "a"), str(blocker / "child.txt"), "x")
        assert result.executed is False
        assert result.event.outcome == "error"
