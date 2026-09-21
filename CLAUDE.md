<!-- GENERATED from rules/agents.yaml by scripts/gen_agent_rules.py. Do not edit. -->

# Selfproof agent rules

For: Claude Code

These rules are generated from rules/agents.yaml. Do not edit the generated files by hand; edit the source and regenerate.

## Rules

- **english-only**: All files, comments, commit messages and documentation are in English. The only exception is tests/fixtures/non_english/.
- **evidence-or-planned**: Every done, correct or secure statement is bound to an executed check on the exact commit, or is labelled planned.
- **no-absolute-claims**: Never write absolutely secure, unhackable, guaranteed or bug-free. The strongest allowed form is zero known findings at a commit per named tools on a date.
- **skipped-is-not-passed**: A missing tool, no network or a timeout is SKIPPED or ERROR, never PASS.
- **branch-and-pr**: After the first commit, never push to main. Small pull requests, one concern each, with a Built-by trailer.
- **protected-paths**: Changes under src/renker_core, src/selfproof/gates, src/selfproof/core, rules, .github, LICENSE, SECURITY.md and CODEOWNERS need a signed human approval.
- **no-weakening**: Never weaken or delete a gate, test or threshold to make something pass. That is refused.
