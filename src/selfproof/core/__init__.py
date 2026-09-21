"""Selfproof core: configuration, the evidence ledger, and the gate runner."""

from __future__ import annotations

from .config import load_config
from .ledger import EvidenceEntry, Ledger, LedgerError
from .runner import RunReport, current_commit, run_gates

__all__ = [
    "load_config",
    "Ledger",
    "EvidenceEntry",
    "LedgerError",
    "RunReport",
    "run_gates",
    "current_commit",
]
