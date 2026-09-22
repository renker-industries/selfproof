"""Render the dashboard as self-contained HTML or a terminal summary.

The HTML export is a single, self-contained file: no CDN, no external script,
no web font. It is designed to read like carefully hand-built software — a
restrained dark theme with a light-mode fallback, a clear type hierarchy,
tabular numerals, and small inline-SVG bars. It conveys no meaning by color
alone (every state also carries a text label), and shows only aggregated
numbers — never file paths, usernames or raw ledger content (concept section 9).

It is installable on phones and desktops via "Add to Home Screen": a web app
manifest and theme color are embedded inline, with no service worker (so the
file stays script-free and fully auditable).
"""

from __future__ import annotations

import html
import json

from .collect import DashboardData

_STATES = ("PASS", "SKIPPED", "FAIL", "ERROR")
_STATE_LABEL = {"PASS": "pass", "SKIPPED": "skipped", "FAIL": "fail", "ERROR": "error"}


_CSS = """
:root{
  --bg:#0a0c10; --panel:#0f1319; --panel-2:#121722; --line:#1e2530;
  --ink:#e8edf4; --ink-2:#9aa7b8; --ink-3:#6b7889;
  --pass:#4ec99a; --skip:#e6b455; --fail:#f0796f; --brand:#7aa2ff;
  --radius:14px; --gap:16px;
  --sans:-apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,Helvetica,Arial,sans-serif;
  --mono:ui-monospace,"SF Mono","Cascadia Code",Menlo,Consolas,monospace;
}
@media (prefers-color-scheme:light){:root:not([data-theme="dark"]){
  --bg:#f6f7f9; --panel:#ffffff; --panel-2:#fbfcfe; --line:#e6e9ef;
  --ink:#111722; --ink-2:#5a6675; --ink-3:#8b97a6;
  --pass:#1a9d6b; --skip:#b9812a; --fail:#d1544a; --brand:#3f6fe0;
}}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);
  font-family:var(--sans);font-size:15px;line-height:1.5;
  -webkit-font-smoothing:antialiased}
.wrap{max-width:900px;margin:0 auto;padding:40px 16px 64px}
header{display:flex;align-items:baseline;justify-content:space-between;
  gap:16px;flex-wrap:wrap;margin-bottom:28px}
.brand{display:flex;align-items:center;gap:10px;font-weight:650;
  letter-spacing:-.02em;font-size:20px}
.dot{width:10px;height:10px;border-radius:50%;
  background:radial-gradient(circle at 30% 30%,var(--brand),#3550b0)}
.tag{font-family:var(--mono);font-size:12px;color:var(--ink-3);
  border:1px solid var(--line);border-radius:999px;padding:3px 10px}
.meta{font-family:var(--mono);font-size:12px;color:var(--ink-3)}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:var(--gap)}
.card{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);
  padding:18px 18px 16px;position:relative;overflow:hidden}
.card.primary::before{content:"";position:absolute;inset:0 0 auto 0;height:2px;
  background:linear-gradient(90deg,var(--brand),transparent 70%)}
.card .n{font-family:var(--mono);font-variant-numeric:tabular-nums;
  font-size:30px;font-weight:600;letter-spacing:-.02em;line-height:1.1}
.card .l{color:var(--ink-2);font-size:13px;margin-top:6px}
.card .s{color:var(--ink-3);font-size:12px;margin-top:2px}
section{margin-top:32px}
h2{font-size:13px;text-transform:uppercase;letter-spacing:.08em;
  color:var(--ink-3);font-weight:600;margin:0 0 14px}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);
  padding:8px 4px}
.row{display:grid;grid-template-columns:132px 1fr auto;align-items:center;
  gap:14px;padding:11px 16px}
.row+.row{border-top:1px solid var(--line)}
.gate{font-family:var(--mono);font-size:13px;color:var(--ink)}
.counts{font-family:var(--mono);font-size:12px;color:var(--ink-2);
  font-variant-numeric:tabular-nums;white-space:nowrap}
.bar{width:100%;height:10px;border-radius:6px;overflow:hidden;
  background:var(--panel-2);display:flex}
.seg{height:100%}
.seg.PASS{background:var(--pass)} .seg.SKIPPED{background:var(--skip)}
.seg.FAIL{background:var(--fail)} .seg.ERROR{background:var(--fail)}
.share{height:12px;border-radius:7px;overflow:hidden;background:var(--panel-2);display:flex}
.share .agent{background:var(--brand)} .share .human{background:var(--ink-3)}
.legend{display:flex;gap:16px;flex-wrap:wrap;margin-top:12px;
  font-size:12px;color:var(--ink-2)}
.legend span{display:inline-flex;align-items:center;gap:6px}
.sw{width:9px;height:9px;border-radius:3px;display:inline-block}
.note{color:var(--skip);font-size:13px;margin-top:14px}
footer{margin-top:36px;color:var(--ink-3);font-size:12px;
  border-top:1px solid var(--line);padding-top:16px}
a{color:var(--brand)}
:focus-visible{outline:2px solid var(--brand);outline-offset:2px}
"""


def _share_pct(data: DashboardData) -> str:
    share = data.self_built_share
    return "no commits" if share is None else f"{share * 100:.0f}% agent-built"


def _kpi_cards(data: DashboardData) -> str:
    esc = html.escape
    share = data.self_built_share
    share_big = "—" if share is None else f"{share * 100:.0f}%"
    share_sub = "no commits yet" if share is None else "agent share of commits"
    token_big = "—" if data.bench_percent is None else f"{data.bench_percent:.0f}%"
    cards = [
        ("primary", str(data.total_checks), "Checks recorded", "on the tamper-evident ledger"),
        ("", str(data.prevented), "Prevented", "bad changes a gate blocked"),
        ("", share_big, "Self-built", share_sub),
        ("", token_big, "Token saving", esc(data.bench_summary)),
    ]
    out = []
    for cls, n, label, sub in cards:
        out.append(
            f'<div class="card {cls}"><div class="n">{esc(n)}</div>'
            f'<div class="l">{esc(label)}</div><div class="s">{esc(sub)}</div></div>'
        )
    return '<div class="cards">' + "".join(out) + "</div>"


def _gate_rows(data: DashboardData) -> str:
    esc = html.escape
    if not data.by_gate:
        return (
            '<div class="panel"><div class="row">'
            '<span class="gate">no records yet</span></div></div>'
        )
    rows = []
    for gate in sorted(data.by_gate):
        counts = data.by_gate[gate]
        total = sum(counts.values()) or 1
        segs = ""
        for state in _STATES:
            n = counts.get(state, 0)
            if n:
                pct = 100 * n / total
                segs += f'<span class="seg {state}" style="width:{pct:.4f}%"></span>'
        label = ", ".join(f"{_STATE_LABEL[s]} {counts[s]}" for s in _STATES if counts.get(s))
        rows.append(
            f'<div class="row"><span class="gate">{esc(gate)}</span>'
            f'<span class="bar" role="img" aria-label="{esc(gate)}: {esc(label)}">{segs}</span>'
            f'<span class="counts">{esc(label)}</span></div>'
        )
    return '<div class="panel">' + "".join(rows) + "</div>"


def _share_section(data: DashboardData) -> str:
    agent, human = data.agent_commits, data.human_commits
    total = agent + human
    if not total:
        return ""
    a_pct = 100 * agent / total
    h_pct = 100 - a_pct
    return (
        '<section><h2>Self-built share</h2>'
        f'<div class="share" role="img" aria-label="agent {agent} commits, human {human} commits">'
        f'<span class="agent" style="width:{a_pct:.4f}%"></span>'
        f'<span class="human" style="width:{h_pct:.4f}%"></span></div>'
        '<div class="legend">'
        f'<span><i class="sw" style="background:var(--brand)"></i>agent · {agent}</span>'
        f'<span><i class="sw" style="background:var(--ink-3)"></i>human · {human}</span>'
        "</div></section>"
    )


def _manifest() -> str:
    data = {
        "name": "Selfproof dashboard", "short_name": "Selfproof",
        "display": "standalone", "background_color": "#0a0c10",
        "theme_color": "#0a0c10", "start_url": ".",
    }
    return "data:application/manifest+json," + html.escape(json.dumps(data))


def render_html(data: DashboardData) -> str:
    """Return a complete, self-contained, installable HTML dashboard document."""
    esc = html.escape
    legend = (
        '<div class="legend">'
        '<span><i class="sw" style="background:var(--pass)"></i>pass</span>'
        '<span><i class="sw" style="background:var(--skip)"></i>skipped</span>'
        '<span><i class="sw" style="background:var(--fail)"></i>fail</span></div>'
    )
    warn = "".join(f'<p class="note">Note: {esc(w)}</p>' for w in data.warnings)
    gen = esc(data.generated) if data.generated else "this machine's ledger"
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#0a0c10">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Selfproof">
<link rel="manifest" href="{_manifest()}">
<title>Selfproof dashboard</title>
<style>{_CSS}</style></head>
<body><div class="wrap">
<header>
  <div class="brand"><span class="dot"></span>Selfproof</div>
  <span class="tag">self-proving code</span>
</header>
<p class="meta">Aggregated evidence from {gen}. Numbers only — no paths or names.</p>
{_kpi_cards(data)}
<section><h2>Verdicts by gate</h2>{_gate_rows(data)}{legend}</section>
{_share_section(data)}
{warn}
<footer>Every number derives from the tamper-evident evidence ledger; run
<code>selfproof ledger verify</code> to recompute the chain. This page contains
no external resources and no scripts.</footer>
</div></body></html>
"""


def render_terminal(data: DashboardData) -> str:
    """Return a compact dark-terminal-style text summary for local use."""
    lines = [
        "SELFPROOF DASHBOARD",
        f"  checks recorded : {data.total_checks}",
        f"  prevented (FAIL): {data.prevented}",
        f"  self-built share: {_share_pct(data)}",
        f"  token saving    : {data.bench_summary}",
        "  verdicts by gate:",
    ]
    for gate in sorted(data.by_gate):
        counts = ", ".join(f"{v}:{n}" for v, n in sorted(data.by_gate[gate].items()))
        lines.append(f"    {gate:<14} {counts}")
    for warning in data.warnings:
        lines.append(f"  note: {warning}")
    return "\n".join(lines)
