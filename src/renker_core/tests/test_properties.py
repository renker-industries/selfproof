from __future__ import annotations

from pathlib import Path

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from renker_core.audit import AuditError, AuditLog
from renker_core.capabilities import PathScope

_component = st.one_of(
    st.sampled_from(["a", "b", "sub", "..", ".", "scopebase", "scopebase2", "deep"]),
    st.text(alphabet="abcdEF012", min_size=1, max_size=4),
)


def _ground_truth_within(base: Path, target: Path) -> bool:
    try:
        rb = base.resolve()
        rt = target.resolve()
    except (OSError, RuntimeError, ValueError):
        return False
    return rt == rb or rt.is_relative_to(rb)


@settings(max_examples=400, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(components=st.lists(_component, min_size=0, max_size=6))
def test_permits_never_diverges_from_ground_truth(tmp_path, components):
    base = tmp_path / "scopebase"
    scope = PathScope(base=str(base))
    target = base
    for part in components:
        target = target / part
    assert scope.permits(str(target)) == _ground_truth_within(base, target)


@settings(max_examples=150, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(seed=st.integers(min_value=0, max_value=10_000), repl=st.integers(min_value=1, max_value=90))
def test_any_single_byte_mutation_is_detected(tmp_path, seed, repl):
    log = AuditLog(tmp_path / f"audit_{seed}_{repl}.log")
    for i in range(4):
        log.record(
            actor="agent:a",
            action="filesystem.write",
            target=f"/x/{i}",
            capability="cap",
            policy_decision="ALLOW",
            reason="r",
            outcome="success",
        )
    raw = log.log_path.read_text(encoding="utf-8")
    if not raw:
        return
    pos = seed % len(raw)
    original = raw[pos]
    replacement = chr(33 + (repl % 90))
    if replacement == original or original == "\n":
        return
    mutated = raw[:pos] + replacement + raw[pos + 1 :]
    log.log_path.write_text(mutated, encoding="utf-8")
    try:
        log.verify()
        raised = False
    except AuditError:
        raised = True
    assert raised
