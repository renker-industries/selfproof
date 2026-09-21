# Autonomy Charter

This file records the authorization under which the Selfproof autopilot operates.
It is a protected path. After the seed phase it is changeable only by the owner
through a signed commit.

- charter_version: 1
- authorized_by: Sebastian Renker
- authorization source: the autopilot master prompt (delivered in the build
  session on 2026-09-21) plus the owner's explicit in-chat confirmation on
  2026-09-21 selecting "Full autopilot" for A1/A2 and the reversible seed steps.

## Integrity anchors

- Concept file: `docs/CONCEPT.md`
  SHA-256 (of `selfproof-concept.md` as read on 2026-09-21):
  `31274b684cc6080f459ed805d5d734c9d2132a48186fa155ad3a961300593632`
- Autopilot prompt: `docs/prompts/autopilot.md`
  SHA-256: recorded in that file's ledger entry when the file is committed.
  Note (honesty, R1): the prompt was delivered inline in the session, not as a
  file on disk, so the archived copy is "as received in session" and may differ
  in whitespace from the owner's source. This limitation is logged in
  `docs/reports/OWNER_TODO.md`.

## Authorizations (anything not YES is NO)

| Switch | Value | Meaning |
| --- | --- | --- |
| A1 create_private_repo | YES | `renker-industries/selfproof`, private |
| A2 import_renker_core | YES | into the private repo, stays private until A3+A4 |
| A3 relicense_renker_core_apache2 | YES (charter) — **gated at execution** | still subject to the contributor check; a legal change, so executed only with a live owner confirmation |
| A4 make_repo_public | YES (charter) — **gated at execution** | publication happens only after the release-readiness check and a live owner confirmation |
| A5 archive_old_repos | NO | |
| A6 post_launch_texts | NO | posting is never automatic; drafts only |
| A7 auto_merge_tier_a | YES | |
| A8 pre_approved_tier_b_classes | [] | none |
| A9 create_private_holdout_repo | YES | `renker-industries/selfproof-holdout`, private |

**Operator note on A3/A4.** The charter marks A3 and A4 YES, but relicensing is a
legal act and making-public is publication. Per the platform's action boundary
and the owner's standing global rule ("irreversible steps never without explicit
confirmation"), these two are executed only after a live owner OK at the moment,
not on the strength of this file alone. Everything else runs autonomously.

## Repositories in scope

- renker-industries/selfproof
- renker-industries/selfproof-holdout
- read-only: everything else of `sebastianrenker` and `renker-industries`

## Budgets

| Budget | Value |
| --- | --- |
| max_pull_requests_per_day | 10 |
| max_open_pull_requests | 5 |
| max_repair_iterations_per_task | 3 |
| max_consecutive_failures_before_pause | 3 |
| max_improvement_cycles_per_run | 20 |
| token_budget_total | UNSET (usage logged, other budgets apply) |

## Kill switch and breaker

- Kill switch: the file `.selfproof/STOP` ends the run cleanly at the next checkpoint.
- Circuit breaker: after 3 consecutive failed/regressing PRs, auto-merge switches
  off (`.selfproof/PAUSED_AUTOMERGE`), an incident issue is opened, the CUSTOS
  root-cause agent runs, and auto-merge resumes only after a proven fix is merged.
