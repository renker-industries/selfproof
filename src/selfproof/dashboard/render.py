"""Render the dashboard as self-contained HTML or a terminal summary.

The HTML export is fully self-contained: no CDN, no external script or font. It
uses a dark, high-contrast theme, conveys no meaning by color alone (every state
also has a text label), and shows only aggregated numbers — never file paths,
usernames or raw ledger content (concept section 9).
"""

from __future__ import annotations

import html

from .collect import DashboardData

_STYLE = """
:root { --bg:#0b0f14; --fg:#d7e0ea; --muted:#8aa0b2; --line:#1c2733;
        --ok:#3fb27f; --warn:#e0a83d; --bad:#e06c75; }
* { box-sizing: border-box; }
body { margin:0; background:var(--bg); color:var(--fg);
       font: 15px/1.5 ui-monospace, "Cascadia Code", Menlo, Consolas, monospace; }
main { max-width: 880px; margin: 0 auto; padding: 24px 16px; }
h1 { font-size: 20px; margin: 0 0 4px; }
.sub { color: var(--muted); margin: 0 0 20px; }
.cards { display:grid; grid-template-columns: repeat(auto-fit,minmax(180px,1fr)); gap:12px; }
.card { border:1px solid var(--line); border-radius:8px; padding:14px; }
.card .n { font-size: 24px; font-weight: 700; }
.card .l { color: var(--muted); font-size: 13px; }
table { width:100%; border-collapse: collapse; margin-top: 20px; }
th,td { text-align:left; padding:8px 10px; border-bottom:1px solid var(--line); }
th { color: var(--muted); font-weight: 600; }
.tag { font-weight:700; }
.tag.PASS{color:var(--ok);} .tag.FAIL{color:var(--bad);}
.tag.SKIPPED{color:var(--warn);} .tag.ERROR{color:var(--bad);}
.warn { color: var(--warn); margin-top: 16px; }
"""


def _share(data: DashboardData) -> str:
    share = data.self_built_share
    if share is None:
        return "no commits"
    return f"{share * 100:.0f}% agent"


def render_html(data: DashboardData) -> str:
    """Return a complete, self-contained HTML dashboard document."""
    esc = html.escape
    cards = [
        ("Checks recorded", str(data.total_checks)),
        ("Prevented (FAIL)", str(data.prevented)),
        ("Self-built share", _share(data)),
        ("Token saving", "see below"),
    ]
    card_html = "\n".join(
        f'<div class="card"><div class="n">{esc(v)}</div><div class="l">{esc(label)}</div></div>'
        for label, v in cards
    )
    rows = []
    for gate in sorted(data.by_gate):
        counts = data.by_gate[gate]
        cells = " ".join(
            f'<span class="tag {esc(v)}">{esc(v)}:{n}</span>' for v, n in sorted(counts.items())
        )
        rows.append(f"<tr><td>{esc(gate)}</td><td>{cells}</td></tr>")
    warn_html = ""
    if data.warnings:
        warn_html = "".join(f'<p class="warn">Note: {esc(w)}</p>' for w in data.warnings)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Selfproof dashboard</title><style>{_STYLE}</style></head>
<body><main>
<h1>Selfproof dashboard</h1>
<p class="sub">Aggregated evidence from the ledger. Numbers only; no paths or names.</p>
<div class="cards">{card_html}</div>
<p class="sub" style="margin-top:16px">Token saving: {esc(data.bench_summary)}</p>
<table><caption class="sub">Verdicts by gate</caption>
<thead><tr><th>Gate</th><th>Verdicts</th></tr></thead>
<tbody>{''.join(rows) or '<tr><td colspan="2">no records yet</td></tr>'}</tbody></table>
{warn_html}
</main></body></html>
"""


def render_terminal(data: DashboardData) -> str:
    """Return a compact dark-terminal-style text summary for local use."""
    lines = [
        "SELFPROOF DASHBOARD",
        f"  checks recorded : {data.total_checks}",
        f"  prevented (FAIL): {data.prevented}",
        f"  self-built share: {_share(data)}",
        f"  token saving    : {data.bench_summary}",
        "  verdicts by gate:",
    ]
    for gate in sorted(data.by_gate):
        counts = ", ".join(f"{v}:{n}" for v, n in sorted(data.by_gate[gate].items()))
        lines.append(f"    {gate:<14} {counts}")
    for warning in data.warnings:
        lines.append(f"  note: {warning}")
    return "\n".join(lines)
