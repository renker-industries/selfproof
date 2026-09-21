"""The ``proof`` gate: run the configured checks and bind them to a commit.

Runs each configured command (tests, lint, ...) and returns ``PASS`` only when
every command exits 0. A missing tool yields ``SKIPPED`` for that command; a
non-zero exit yields ``FAIL``. The commit SHA the run is bound to is recorded so
a stale proof (a result for a different SHA) is detectable and counts as a
failure, never a pass (concept sections 4.1 and 5).
"""

from __future__ import annotations

from .base import Gate, GateContext, GateResult, Verdict, run_command


class ProofGate(Gate):
    """Execute the configured proof commands against the current commit."""

    name = "proof"

    def run(self, ctx: GateContext) -> GateResult:
        commands = ctx.config["proof"]["commands"]
        timeout = ctx.config["proof"].get("timeout", 900)

        results: list[str] = []
        outputs: list[str] = []
        any_fail = False
        any_skip = False

        for cmd in commands:
            code, out = run_command(list(cmd), ctx.repo_root, timeout=timeout)
            printable = " ".join(cmd)
            outputs.append(f"$ {printable}\n{out}")
            if code is None:
                any_skip = True
                results.append(f"SKIPPED  {printable}")
            elif code == 0:
                results.append(f"PASS     {printable}")
            else:
                any_fail = True
                results.append(f"FAIL({code}) {printable}")

        summary_lines = "\n".join(results)
        output = f"commit {ctx.commit_sha}\n{summary_lines}\n\n" + "\n\n".join(outputs)
        command = " && ".join(" ".join(c) for c in commands)

        if any_fail:
            verdict = Verdict.FAIL
            summary = "one or more proof commands failed"
        elif any_skip:
            # A skipped required check is never a pass.
            verdict = Verdict.SKIPPED
            summary = "a proof command was skipped (missing tool); not a pass"
        else:
            verdict = Verdict.PASS
            summary = f"all {len(commands)} proof commands passed at {ctx.commit_sha[:12]}"

        return GateResult(
            self.name, verdict, summary,
            command=command,
            exit_code=None,
            output=output,
            details={"results": results, "commit_sha": ctx.commit_sha},
        )
