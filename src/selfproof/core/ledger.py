"""The evidence ledger, built on the kernel's tamper-evident audit chain.

Selfproof does not invent a second ledger format. It reuses
``renker_core.AuditLog`` -- an append-only JSONL file with a SHA-256 hash chain
and a ``verify()`` that recomputes it (concept section 4.3). The richer
Selfproof evidence schema (gate, command, exit code, output hash, stage, ...) is
stored as canonical JSON inside the chained ``reason`` field, so the chain hash
covers every field and tamper-evidence extends to all of them.

Honest limit: a hash chain detects edited entries, not a truncated tail. Anchor
the chain head in every signed release tag (see :meth:`Ledger.head`).
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from renker_core import AuditError, AuditLog


@dataclass(frozen=True)
class EvidenceEntry:
    """One recorded piece of evidence (concept section 4.3)."""

    id: str
    timestamp: str
    actor_kind: str  # human | agent | ci
    actor_name: str
    commit_sha: str
    gate: str
    command: str
    exit_code: int | None
    output_sha256: str
    verdict: str
    stage: str  # seed | self-hosted | protected
    prev_hash: str
    hash: str


class LedgerError(Exception):
    """Raised when the ledger cannot be read or fails verification."""


class Ledger:
    """A thin wrapper over ``renker_core.AuditLog`` for Selfproof evidence."""

    def __init__(self, path: str | Path) -> None:
        """Open (or create on first write) the ledger at ``path``.

        Args:
            path: Path to the append-only JSONL evidence file.
        """
        self.path = Path(path)
        self._log = AuditLog(self.path)

    def record(
        self,
        *,
        actor_kind: str,
        actor_name: str,
        commit_sha: str,
        gate: str,
        command: str,
        exit_code: int | None,
        output_sha256: str,
        verdict: str,
        stage: str,
        decision_id: str | None = None,
    ) -> EvidenceEntry:
        """Append one evidence entry and return it with its chain hashes.

        The full Selfproof payload is packed into the chained ``reason`` field
        as canonical JSON; the kernel computes and stores ``prev_hash`` and
        ``entry_hash`` over it.
        """
        payload = {
            "actor_kind": actor_kind,
            "actor_name": actor_name,
            "commit_sha": commit_sha,
            "gate": gate,
            "command": command,
            "exit_code": exit_code,
            "output_sha256": output_sha256,
            "verdict": verdict,
            "stage": stage,
        }
        event = self._log.record(
            actor=f"{actor_kind}:{actor_name}",
            action=gate,
            target=commit_sha,
            capability=stage,
            policy_decision=verdict,
            reason=json.dumps(payload, sort_keys=True, separators=(",", ":")),
            outcome=output_sha256,
            resource=commit_sha,
            decision_id=decision_id,
        )
        return EvidenceEntry(
            id=event.event_id,
            timestamp=event.timestamp,
            prev_hash=event.prev_hash,
            hash=event.entry_hash,
            **payload,
        )

    def read_all(self) -> list[EvidenceEntry]:
        """Return every evidence entry in order, reconstructed from the chain."""
        entries: list[EvidenceEntry] = []
        for event in self._log.read_all():
            try:
                payload = json.loads(event.reason)
            except (ValueError, TypeError) as error:
                raise LedgerError(
                    f"corrupt evidence payload in {event.event_id}: {error}"
                ) from error
            entries.append(
                EvidenceEntry(
                    id=event.event_id,
                    timestamp=event.timestamp,
                    prev_hash=event.prev_hash,
                    hash=event.entry_hash,
                    **payload,
                )
            )
        return entries

    def verify(self) -> None:
        """Recompute the hash chain. Raise :class:`LedgerError` if it is broken."""
        try:
            self._log.verify()
        except AuditError as error:
            raise LedgerError(str(error)) from error

    def head(self) -> str:
        """Return the current chain head (the last entry's hash, or genesis)."""
        entries = self.read_all()
        return entries[-1].hash if entries else "0" * 64

    def as_jsonl(self) -> str:
        """Return the ledger as JSON lines of Selfproof evidence entries."""
        return "\n".join(json.dumps(asdict(e)) for e in self.read_all())
