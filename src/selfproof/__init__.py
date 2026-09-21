"""Selfproof: a provider-neutral platform that proves AI-written code.

Selfproof runs gates over code changes, records every result as tamper-evident
evidence on the kernel's audit chain, and builds itself through a controlled
loop. Its kernel is ``renker_core``.

Nothing in this package promises "absolute" security. Every check reports one of
four honest verdicts (see :mod:`selfproof.gates.base`) and a missing tool is
never reported as a pass.
"""

__version__ = "0.0.0"

__all__ = ["__version__"]
