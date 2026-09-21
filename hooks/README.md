# Git hooks

Versioned hooks enforced at commit and push time (adapter level L1).

Enable them once per clone:

```bash
git config core.hooksPath hooks
chmod +x hooks/commit-msg hooks/pre-commit hooks/pre-push
```

| Hook | Enforces |
| --- | --- |
| `commit-msg` | a `Built-by: human` or `Built-by: agent <name> <version>` trailer |
| `pre-commit` | the `language` gate over tracked files |
| `pre-push` | all gates and `ledger verify` |

Hooks require `python` on PATH and run with `PYTHONPATH=src:src/renker_core`.
