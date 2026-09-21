"""The Selfproof dashboard (concept section 9).

Reads only from the evidence ledger, git and the token benchmarks, and renders
either a self-contained HTML export or a terminal summary. Every number is
derived from recorded evidence; the export shows aggregated numbers only.
"""

from __future__ import annotations

from .collect import DashboardData, collect
from .render import render_html, render_terminal

__all__ = ["DashboardData", "collect", "render_html", "render_terminal"]
