from __future__ import annotations

import importlib

import renker_core


def test_version_present():
    assert isinstance(renker_core.__version__, str)
    assert renker_core.__version__


def test_all_primitives_importable():
    for name in renker_core.PRIMITIVES:
        module = importlib.import_module(f"renker_core.{name}")
        assert module.PRIMITIVE == name


def test_crypto_interface_exposes_protocols():
    crypto = importlib.import_module("renker_core.crypto_interface")
    for symbol in ("Encryptor", "Signer", "Verifier"):
        assert hasattr(crypto, symbol)
