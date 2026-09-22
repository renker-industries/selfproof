# Configuration reference

Selfproof reads `selfproof.toml` at the repository root and falls back to
built-in defaults. All keys are optional.

| Key | Type | Default | Meaning |
| --- | --- | --- | --- |
| `stage` | string | `seed` | Ledger stage tag: `seed`, `self-hosted` or `protected`. |
| `ledger.path` | string | `docs/reports/ledger.jsonl` | Where the evidence ledger is written. |
| `proof.commands` | list of lists | `pytest -q`, `ruff check .` | Commands the `proof` gate runs and binds to the commit. Each must exit 0 for a PASS. |
| `proof.timeout` | int | `900` | Seconds before a proof command is killed. |
| `language.exclude` | list | fixtures, corpora, kernel, gate data | Path prefixes excluded from the English-only scan. |
| `language.text_suffixes` | list | `.py .md .toml …` | File suffixes treated as text. |
| `slop.exclude` | list | kernel, corpora, fixtures | Path prefixes excluded from the slop scan. |
| `architecture.file_max_lines` | int | `400` | Per-file line budget. |
| `architecture.func_max_lines` | int | `80` | Per-function line budget. |
| `architecture.package_root` | string | `src/selfproof` | Package the architecture gate inspects. |

Security note: loosening a budget or removing an exclude widens what the gates
accept. Such changes are visible in the diff and, under protected paths, need a
signed approval.

## Try it
```bash
selfproof status
```
