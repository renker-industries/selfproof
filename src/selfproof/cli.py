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
from .dashboard import collect, render_html, render_terminal
from .fleet import report as fleet_report
from .fleet import scan as fleet_scan
from .release import readiness, sbom
from .tokens import aggregate, load_records, report


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


def _cmd_bench_report(_: argparse.Namespace) -> int:
    stats = aggregate(load_records(_repo_root() / "docs" / "reports" / "benchmarks"))
    print(report(stats))
    return 0


def _cmd_dashboard_show(_: argparse.Namespace) -> int:
    print(render_terminal(collect(_repo_root())))
    return 0


def _cmd_dashboard_export(args: argparse.Namespace) -> int:
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_html(collect(_repo_root())), encoding="utf-8")
    print(f"wrote {out}")
    return 0


def _cmd_dashboard_open(_: argparse.Namespace) -> int:
    import tempfile
    import webbrowser

    html_text = render_html(collect(_repo_root()))
    path = Path(tempfile.gettempdir()) / "selfproof-dashboard.html"
    path.write_text(html_text, encoding="utf-8")
    print(f"opening {path}")
    webbrowser.open(path.as_uri())
    return 0


def _cmd_release_check(_: argparse.Namespace) -> int:
    problems = readiness(_repo_root())
    if problems:
        print("NOT release-ready:")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("release-ready: all required gates PASS, ledger verified, rules current, files present")
    return 0


def _cmd_release_sbom(args: argparse.Namespace) -> int:
    import json

    text = json.dumps(sbom(_repo_root()), indent=2)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        print(text)
    return 0


def _cmd_fleet_scan(_: argparse.Namespace) -> int:
    print(fleet_report(fleet_scan(["renker-industries", "sebastianrenker"])))
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

    p_dash = sub.add_parser("dashboard", help="render the evidence dashboard")
    dash_sub = p_dash.add_subparsers(dest="dashboard_command", required=True)
    p_dash_show = dash_sub.add_parser("show", help="print a terminal dashboard summary")
    p_dash_show.set_defaults(func=_cmd_dashboard_show)
    p_dash_export = dash_sub.add_parser("export", help="write the self-contained HTML dashboard")
    p_dash_export.add_argument("--out", required=True, help="output HTML file path")
    p_dash_export.set_defaults(func=_cmd_dashboard_export)
    p_dash_open = dash_sub.add_parser("open", help="build and open the dashboard in your browser")
    p_dash_open.set_defaults(func=_cmd_dashboard_open)

    p_release = sub.add_parser("release", help="release readiness and SBOM")
    release_sub = p_release.add_subparsers(dest="release_command", required=True)
    p_release_check = release_sub.add_parser("check", help="fail unless the build is release-ready")
    p_release_check.set_defaults(func=_cmd_release_check)
    p_release_sbom = release_sub.add_parser("sbom", help="print or write a minimal SBOM")
    p_release_sbom.add_argument("--out", default="", help="write the SBOM to this file")
    p_release_sbom.set_defaults(func=_cmd_release_sbom)

    p_fleet = sub.add_parser("fleet", help="fleet-wide repository operations")
    fleet_sub = p_fleet.add_subparsers(dest="fleet_command", required=True)
    p_fleet_scan = fleet_sub.add_parser("scan", help="list and classify repos of both accounts")
    p_fleet_scan.set_defaults(func=_cmd_fleet_scan)

    p_bench = sub.add_parser("bench", help="token benchmark operations")
    bench_sub = p_bench.add_subparsers(dest="bench_command", required=True)
    p_bench_report = bench_sub.add_parser("report", help="report net token saving from benchmarks")
    p_bench_report.set_defaults(func=_cmd_bench_report)

    p_auto = sub.add_parser("autopilot", help="run one gate cycle, honoring the kill switch")
    p_auto.add_argument("--gates", default="", help="comma-separated gate names (default: all)")
    p_auto.set_defaults(func=_cmd_autopilot)

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Returns a process exit code.

    With no arguments (for example when the packaged binary is double-clicked),
    it defaults to opening the dashboard, so the simplest use needs no typing.
    """
    effective = sys.argv[1:] if argv is None else argv
    if not effective:
        effective = ["dashboard", "open"]
    parser = build_parser()
    args = parser.parse_args(effective)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
