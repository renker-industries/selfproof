"""Gate registry. Each gate name maps to its implementation class.

Seed gates: ``language`` and ``proof`` (concept phase 1). The remaining gates
(``slop``, ``architecture``, ``security``, ``docs_claims``, ``docs_coverage``,
``test_weakening``) are built through the loop in phase 2.
"""

from __future__ import annotations

from .base import Gate, GateContext, GateResult, Verdict
from .language import LanguageGate
from .proof import ProofGate

GATES: dict[str, type[Gate]] = {
    LanguageGate.name: LanguageGate,
    ProofGate.name: ProofGate,
}

__all__ = ["Gate", "GateContext", "GateResult", "Verdict", "GATES"]
