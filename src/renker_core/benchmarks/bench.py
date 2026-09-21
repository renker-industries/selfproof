from __future__ import annotations

import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from renker_core.audit import AuditLog
from renker_core.capabilities import Capability, CapabilityStore, PathScope
from renker_core.identity import Actor
from renker_core.policy import evaluate


def _timed(label: str, iterations: int, fn) -> None:
    start = time.perf_counter()
    for _ in range(iterations):
        fn()
    elapsed = time.perf_counter() - start
    per_op_us = (elapsed / iterations) * 1_000_000
    ops_per_s = iterations / elapsed
    print(
        f"{label:<28} {per_op_us:8.2f} us/op   {ops_per_s:12,.0f} ops/s   (n={iterations:,})",
        flush=True,
    )


def main() -> None:
    workdir = Path(tempfile.mkdtemp(prefix="renker_bench_"))
    now = datetime.now(timezone.utc)
    scope = PathScope(base=str(workdir / "drafts"))

    store = CapabilityStore()
    store.grant(
        Capability(
            capability="filesystem.write",
            scope=scope,
            granted_to="agent:a",
            granted_by="human:sebastian",
            issued_at=now,
            expires_at=now + timedelta(hours=1),
        )
    )
    actor = Actor("agent", "a")
    target = str(workdir / "drafts" / "f.txt")

    print("renker-core micro-benchmarks (single core, warm)")
    print("-" * 78)
    _timed("identity_creation", 100_000, lambda: Actor("agent", "a"))
    _timed("scope_permits", 5_000, lambda: scope.permits(target))
    _timed(
        "policy_evaluate",
        3_000,
        lambda: evaluate(actor=actor, action="filesystem.write", target=target, store=store),
    )

    audit = AuditLog(workdir / "audit.log")

    def append() -> None:
        audit.record(
            actor="agent:a",
            action="filesystem.write",
            target=target,
            capability="cap",
            policy_decision="ALLOW",
            reason="ok",
            outcome="success",
        )

    _timed("audit_append_fsync", 500, append)
    n = len(audit.read_all())
    _timed("audit_verify_full", 30, audit.verify)
    _timed("audit_query_by_actor", 100, lambda: audit.query(actor="agent:a"))
    print("-" * 78)
    print(f"audit chain length verified: {n:,} events")


if __name__ == "__main__":
    main()
