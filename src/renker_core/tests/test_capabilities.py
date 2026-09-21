from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from renker_core.capabilities import Capability, CapabilityError, CapabilityStore, PathScope


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


def test_scope_permits_inside(tmp_path):
    scope = PathScope(base=str(tmp_path / "drafts"))
    assert scope.permits(str(tmp_path / "drafts" / "note.txt"))


def test_scope_rejects_traversal(tmp_path):
    scope = PathScope(base=str(tmp_path / "drafts"))
    assert not scope.permits(str(tmp_path / "drafts" / ".." / "secret.txt"))


def test_scope_rejects_prefix_confusion(tmp_path):
    scope = PathScope(base=str(tmp_path / "Documents"))
    assert not scope.permits(str(tmp_path / "Documents2" / "x.txt"))


def test_scope_rejects_sibling(tmp_path):
    scope = PathScope(base=str(tmp_path / "drafts"))
    assert not scope.permits(str(tmp_path / "other" / "x.txt"))


def test_capability_id_is_stable(tmp_path):
    a = _cap(tmp_path)
    b = _cap(tmp_path, issued_at=a.issued_at)
    assert a.capability_id == b.capability_id
    assert a.capability_id.startswith("cap_")


def test_expiry(tmp_path):
    past = datetime.now(timezone.utc) - timedelta(hours=1)
    cap = _cap(tmp_path, issued_at=past - timedelta(hours=1), expires_at=past)
    assert cap.is_expired()


def test_naive_datetime_rejected(tmp_path):
    with pytest.raises(CapabilityError):
        _cap(tmp_path, issued_at=datetime.now())


def test_capability_requires_dotted_verb(tmp_path):
    with pytest.raises(CapabilityError):
        _cap(tmp_path, capability="filesystem")


def test_store_grant_find_revoke(tmp_path):
    store = CapabilityStore()
    cap = _cap(tmp_path)
    cid = store.grant(cap)
    assert store.find("agent:a", "filesystem.write") == [cap]
    assert store.revoke(cid) is True
    assert store.is_revoked(cid) is True


def test_store_cannot_revoke_non_revocable(tmp_path):
    store = CapabilityStore()
    cap = _cap(tmp_path, revocable=False)
    cid = store.grant(cap)
    assert store.revoke(cid) is False
    assert store.is_revoked(cid) is False
