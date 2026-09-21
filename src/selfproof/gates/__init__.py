"""Gate registry. Each gate name maps to its implementation class.

Seed gates (phase 1): ``language``, ``proof``. Phase 2 adds ``slop``,
``architecture`` and ``test_weakening``. Still to come: ``security``,
``docs_claims``, ``docs_coverage``.
"""

from __future__ import annotations

from .architecture import ArchitectureGate
from .base import Gate, GateContext, GateResult, Verdict
from .language import LanguageGate
from .proof import ProofGate
from .slop import SlopGate
from .test_weakening import TestWeakeningGate

GATES: dict[str, type[Gate]] = {
    LanguageGate.name: LanguageGate,
    ProofGate.name: ProofGate,
    SlopGate.name: SlopGate,
    ArchitectureGate.name: ArchitectureGate,
    TestWeakeningGate.name: TestWeakeningGate,
}

__all__ = ["Gate", "GateContext", "GateResult", "Verdict", "GATES"]
