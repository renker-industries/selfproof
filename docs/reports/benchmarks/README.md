# Token benchmarks

Each `*.jsonl` file in this directory holds one benchmark record per line:

```json
{"task": "add-a-gate", "model": "claude-opus-4-8", "baseline_tokens": {"input": 1200, "output": 900}, "actual_tokens": {"input": 1000, "output": 500}, "overhead_tokens": 120}
```

`selfproof bench report` aggregates them. Below n=5 it shows `insufficient data`
and no percentage; below n=20, `preliminary`. Unmeasured runs (missing token
data) are counted separately, never as zero. No real runs are recorded yet.
