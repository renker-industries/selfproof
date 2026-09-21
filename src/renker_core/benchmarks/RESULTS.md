# Benchmark results — renker-core

Reproducible micro-benchmarks for the authorization hot path. These are **real,
single-machine** numbers, not marketing figures. Re-run and replace when the
environment or code changes.

## How to reproduce

```bash
pip install -e ".[dev]"
python benchmarks/bench.py
```

## Environment

| Field | Value |
|---|---|
| Date | 2026-09-16 |
| Python | 3.12.10 |
| OS / arch | Windows 11, AMD64 |
| Mode | single core, warm process |
| Runs | 1 (see per-op `n` below); not yet averaged over multiple processes |

## Results

| Operation | µs/op | ops/s | n |
|---|--:|--:|--:|
| `identity_creation` | 0.73 | 1,375,321 | 100,000 |
| `scope_permits` | 497.26 | 2,011 | 5,000 |
| `policy_evaluate` (end-to-end decision) | 732.88 | 1,364 | 3,000 |
| `audit_append_fsync` | 8,628.97 | 116 | 500 |
| `audit_verify_full` (500-entry chain) | 5,290.24 | 189 | 30 |
| `audit_query_by_actor` | 2,831.09 | 353 | 100 |

## Honest reading of these numbers

- **A full authorization decision is ~0.73 ms** on this machine (`policy_evaluate`),
  dominated by `scope_permits` (~0.5 ms). This is **not** "blazing fast": the scope
  check calls `Path.resolve()`, which hits the filesystem. This is a deliberate
  correctness/robustness trade-off (real path normalization beats string tricks),
  and it is the obvious first target if latency ever matters. See ROADMAP.
- **Audit append is fsync-bound (~8.6 ms/op → ~116 appends/s).** Durability, not
  speed, is the design goal. Batching/async fsync is a future option, not a claim.
- **These are single-process, single-run figures.** No multi-process aggregation,
  no percentile distribution. Do not cite a percentile that was not measured.
