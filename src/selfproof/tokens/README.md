# `selfproof.tokens`

Honest token-saving measurement for the token layer (RENKER FLINT).

- **Purpose:** compute the net saving (`baseline - actual - overhead`) from
  paired control runs, with sample size and method.
- **Boundaries:** it reports only what benchmark files contain; it invents no
  numbers and treats an unmeasured run as `unmeasured`, never zero.
- **Must not:** show a saving percentage that is not generated from a benchmark
  file, or count an unmeasured run in the statistics.

| Module | Purpose |
| --- | --- |
| `meter.py` | token usage record and the net-saving formula |
| `bench.py` | load benchmark JSONL, aggregate, and render an honest report |

Benchmark files live in `docs/reports/benchmarks/*.jsonl`. Below `n = 5` the
report shows `insufficient data` and no percentage; below `n = 20` it is
`preliminary`. Run `selfproof bench report`.
