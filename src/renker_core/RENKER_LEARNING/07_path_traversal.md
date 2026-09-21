# 07 — Path Traversal (and prefix confusion)

## Concept
**Path traversal** uses `..` (or symlinks, or absolute paths) to escape an allowed directory:
`~/Documents/drafts/../../.ssh/id_rsa`. **Prefix confusion** exploits naive string checks:
`~/Documents2` starts with the string `~/Documents` but is a different directory.

## Why it exists as a defense
The single most common way a scoped file permission is defeated is a bad path comparison. If the scope
check is wrong, every other layer is moot.

## Architecture
- `renker_core/capabilities/model.py: PathScope`
  - `permits(target)`: `Path(target).expanduser().resolve()` — `resolve()` collapses `..` **before**
    the check, so traversal is normalized away.
  - `_is_within(target, base)`: compares **resolved path parts** (`target.parts[:len(base.parts)] ==
    base.parts`), never a string prefix. This is what defeats `Documents2` vs `Documents`.
  - Equal path is allowed (the base itself); a target with fewer/equal parts than base is rejected.

## Security implications
Doing the containment check on normalized `Path.parts` closes both traversal and prefix confusion in
one place. String `startswith` would pass `Documents2`; part comparison does not.

## Failure modes
- Comparing raw strings instead of resolved parts (prefix confusion returns).
- Checking before resolving (traversal `..` slips through).
- On Windows, case and separators — `resolve()` normalizes these.

## Tests
`tests/test_capabilities.py`: `test_scope_rejects_traversal`, `test_scope_rejects_prefix_confusion`,
`test_scope_rejects_sibling`. End-to-end in `tests/test_security_attacks.py` (`test_attack_path_traversal`,
`test_attack_prefix_confusion`) and in `demo/demo_slice.py` (step 4).

## Design trade-offs
`resolve()` touches the filesystem for symlink resolution; acceptable and correct for a local guard.
The alternative (pure lexical normalization) would miss symlink escapes.

---

## Questions (answer before reading the reference)

**Recall**
1. What does `..` do in a path, and what turns it into an escape attack?
2. Why does `Documents2` "match" `Documents` under a naive check?

**Code**
3. Which single call neutralizes `..`, and why must it happen *before* the containment check?
4. What exactly is compared in `_is_within` — strings or parts?

**Debug**
5. You change `_is_within` to `str(target).startswith(str(base))` and a prefix-confusion test fails.
   Explain the failure in one sentence.

**Security**
6. Name one traversal vector that lexical-only normalization would miss but `resolve()` catches.

--- reference ---
1. `..` moves up one directory; it becomes an attack when it moves *above* the allowed scope.
2. Because the string `"…/Documents2"` has the string `"…/Documents"` as a prefix, even though they are
   different directories.
3. `Path(...).resolve()`; before, because it collapses `..` into a concrete path so the containment
   check sees the real destination, not the literal `..`.
4. Resolved path **parts** (tuples of components), not strings.
5. `Documents2` string-starts-with `Documents`, so the naive check wrongly treats a sibling as inside.
6. A symlink inside the scope pointing outside it — `resolve()` follows the link to its real target.
