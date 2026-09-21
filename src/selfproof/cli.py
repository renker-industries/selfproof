"""The ``selfproof`` command-line interface.

Seed commands (concept phase 1):

- ``selfproof status``        current stage, ledger head and recent verdicts
- ``selfproof build``         run the gates against the current commit
- ``selfproof ledger verify`` recompute the evidence hash chain
- ``selfproof autopilot``     run one gate cycle, honoring the kill switch

Later phases extend ``build`` into the full loop and ``autopilot`` into the
headless improvement loop.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .core.config import load_config
from .core.ledger import Ledger, LedgerError
from .core.rules import check_generated, write_generated
from .core.runner import run_gates


def _repo_root() -> Path:
    return Path.cwd()


def _cmd_status(_: argparse.Namespace) -> int:
    root = _repo_root()
    cfg = load_config(root)
    ledger = Ledger(root / cfg["ledger"]["path"])
    entries = ledger.read_all()
    print(f"stage:       {cfg.get('stage', 'seed')}")
    print(f"ledger:      {cfg['ledger']['path']}")
    print(f"entries:     {len(entries)}")
    print(f"chain head:  {ledger.head()}")
    if entries:
        print("recent:")
        for e in entries[-5:]:
            print(f"  {e.timestamp}  {e.gate:<10} {e.verdict:<8} {e.commit_sha[:12]}")
    return 0


def _cmd_build(args: argparse.Namespace) -> int:
    root = _repo_root()
    gate_names = args.gates.split(",") if args.gates else None
    report = run_gates(root, gate_names)
    print(f"commit {report.commit_sha}")
    for r in report.results:
        print(f"  {r.verdict.value:<8} {r.gate:<10} {r.summary}")
        if r.blocking and r.output:
            for line in r.output.splitlines()[:20]:
                print(f"      {line}")
    if report.blocking:
        print("\nRESULT: blocked (a gate failed or errored)")
        return 1
    if report.has_skips:
        print("\nRESULT: passed with SKIPPED checks (not release-ready)")
        return 0
    print("\nRESULT: all gates passed")
    return 0


def _cmd_ledger_verify(_: argparse.Namespace) -> int:
    root = _repo_root()
    cfg = load_config(root)
    ledger = Ledger(root / cfg["ledger"]["path"])
    try:
        ledger.verify()
    except LedgerError as error:
        print(f"LEDGER BROKEN: {error}")
        return 1
    print(f"ledger OK: chain intact, head {ledger.head()}")
    return 0


def _cmd_rules_generate(_: argparse.Namespace) -> int:
    for name in write_generated(_repo_root()):
        print(f"wrote {name}")
    return 0


def _cmd_rules_check(_: argparse.Namespace) -> int:
    drift = check_generated(_repo_root())
    if drift:
        for line in drift:
            print(line)
        print("\nRESULT: generated rules files are out of date")
        return 1
    print("rules OK: CLAUDE.md, AGENTS.md and GEMINI.md match rules/agents.yaml")
    return 0


def _cmd_autopilot(args: argparse.Namespace) -> int:
    root = _repo_root()
    stop = root / ".selfproof" / "STOP"
    if stop.exists():
        print("kill switch present (.selfproof/STOP); stopping cleanly")
        return 0
    print("autopilot: running one gate cycle")
    return _cmd_build(args)


def build_parser() -> argparse.ArgumentParser:
    """Construct the argument parser (also used to generate the CLI reference)."""
    parser = argparse.ArgumentParser(prog="selfproof", description="Prove AI-written code.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_status = sub.add_parser("status", help="show stage, ledger head and recent verdicts")
    p_status.set_defaults(func=_cmd_status)

    p_build = sub.add_parser("build", help="run the gates against the current commit")
    p_build.add_argument("--gates", default="", help="comma-separated gate names (default: all)")
    p_build.set_defaults(func=_cmd_build)

    p_ledger = sub.add_parser("ledger", help="ledger operations")
    ledger_sub = p_ledger.add_subparsers(dest="ledger_command", required=True)
    p_verify = ledger_sub.add_parser("verify", help="recompute the evidence hash chain")
    p_verify.set_defaults(func=_cmd_ledger_verify)

    p_rules = sub.add_parser("rules", help="generate or check the per-agent rules files")
    rules_sub = p_rules.add_subparsers(dest="rules_command", required=True)
    p_rules_gen = rules_sub.add_parser("generate", help="write CLAUDE.md, AGENTS.md, GEMINI.md")
    p_rules_gen.set_defaults(func=_cmd_rules_generate)
    p_rules_check = rules_sub.add_parser("check", help="fail if a generated rules file is stale")
    p_rules_check.set_defaults(func=_cmd_rules_check)

    p_auto = sub.add_parser("autopilot", help="run one gate cycle, honoring the kill switch")
    p_auto.add_argument("--gates", default="", help="comma-separated gate names (default: all)")
    p_auto.set_defaults(func=_cmd_autopilot)

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Returns a process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
