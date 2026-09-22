# `selfproof.fleet`

Read-only enumeration of the owner's repositories across both accounts.

- **Purpose:** list and classify every repository (in write-scope vs read-only)
  so the dashboard can show fleet coverage.
- **Boundaries:** read-only; it uses `gh` to list repositories and never writes
  to any repository. Only the two charter repositories are ever in write-scope.
- **Must not:** invent findings. A finding counts as "improved" only with a
  recorded before entry, a fix commit and an after entry.

Cross-repository gate scanning and before/after "improved" tracking are not
implemented yet; `report()` states that limit. Run `selfproof fleet scan`.
