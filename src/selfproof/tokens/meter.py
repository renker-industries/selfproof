"""Token usage measurement (concept section 8).

Reads token counts from a normalized record and computes the net saving of the
token layer honestly: ``baseline - actual - overhead``. No number is invented;
if an agent reports no usage data, its tokens are ``None`` (``unmeasured``) and
never treated as zero.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TokenUsage:
    """Input and output token counts for one run.

    ``None`` means the agent reported no usage for that field; it is
    ``unmeasured`` and must never be treated as zero.
    """

    input: int | None
    output: int | None

    @property
    def total(self) -> int | None:
        """Return input+output, or ``None`` if either part is unmeasured."""
        if self.input is None or self.output is None:
            return None
        return self.input + self.output

    @classmethod
    def from_dict(cls, data: dict | None) -> TokenUsage:
        """Build a usage from a ``{"input": .., "output": ..}`` dict (or None)."""
        if not data:
            return cls(input=None, output=None)
        return cls(input=data.get("input"), output=data.get("output"))


def net_saving(baseline: TokenUsage, actual: TokenUsage, overhead: int) -> int | None:
    """Return ``baseline.total - actual.total - overhead``, or ``None``.

    Returns ``None`` when either run is unmeasured, so an unmeasured run can
    never produce a fake saving.

    Args:
        baseline: Tokens for the control run (no token layer).
        actual: Tokens for the run with the token layer.
        overhead: The token layer's own overhead, in tokens.
    """
    if baseline.total is None or actual.total is None:
        return None
    return baseline.total - actual.total - overhead
