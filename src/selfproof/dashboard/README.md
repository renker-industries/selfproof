# `selfproof.dashboard`

Renders recorded evidence as a dashboard (concept section 9).

- **Purpose:** show, from the ledger alone, how many checks ran, what was
  prevented, the self-built share and the net token saving.
- **Boundaries:** reads only the ledger, git and the token benchmarks; invents
  no numbers. The HTML export is self-contained (no CDN) and shows aggregated
  numbers only — never file paths, usernames or raw ledger content.
- **Must not:** leak private repository names or details into the static export.

| Module | Purpose |
| --- | --- |
| `collect.py` | gather metrics from the ledger, git and benchmarks |
| `render.py` | self-contained HTML export and a terminal summary |

Commands: `selfproof dashboard show` (terminal), `selfproof dashboard export
--out <file>` (static HTML for GitHub Pages).
