from __future__ import annotations

import pytest

from renker_core.identity import Actor, IdentityError


def test_urn_roundtrip():
    actor = Actor(kind="agent", identifier="rencora-session-8f2c")
    assert actor.urn == "agent:rencora-session-8f2c"
    assert Actor.from_urn(actor.urn) == actor


def test_reject_unknown_kind():
    with pytest.raises(IdentityError):
        Actor(kind="robot", identifier="x")


def test_reject_identifier_with_colon():
    with pytest.raises(IdentityError):
        Actor(kind="agent", identifier="a:b")


def test_reject_identifier_with_whitespace():
    with pytest.raises(IdentityError):
        Actor(kind="agent", identifier="a b")


def test_reject_empty_identifier():
    with pytest.raises(IdentityError):
        Actor(kind="human", identifier="")


def test_from_urn_rejects_malformed():
    with pytest.raises(IdentityError):
        Actor.from_urn("agentnocolon")
