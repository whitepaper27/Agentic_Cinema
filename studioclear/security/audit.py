"""Tamper-evident audit log (sol.md §19 + E8.3).

Append-only hash chain: each event stores
    hash = sha256(prev_hash + canonical_json(event_body))
so any later edit or deletion breaks verification. Pure and unit-tested
(tests/unit/test_audit_chain.py). For P0 this backs onto a JSON file or memory;
Firestore is a drop-in later (sol.md §11).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field

GENESIS = "0" * 64


def _canonical(body: dict) -> str:
    # Stable serialization so the hash is deterministic regardless of key order.
    return json.dumps(body, sort_keys=True, separators=(",", ":"), default=str)


def _hash(prev_hash: str, body: dict) -> str:
    return hashlib.sha256((prev_hash + _canonical(body)).encode("utf-8")).hexdigest()


@dataclass
class AuditEvent:
    body: dict
    prev_hash: str
    hash: str


@dataclass
class AuditLog:
    """In-memory append-only hash chain. `events[i].hash` chains from `events[i-1]`."""

    events: list[AuditEvent] = field(default_factory=list)

    @property
    def head(self) -> str:
        return self.events[-1].hash if self.events else GENESIS

    def append(self, body: dict) -> AuditEvent:
        prev = self.head
        event = AuditEvent(body=body, prev_hash=prev, hash=_hash(prev, body))
        self.events.append(event)
        return event

    def verify(self) -> bool:
        """Recompute the whole chain; return False if anything was tampered with."""
        prev = GENESIS
        for event in self.events:
            if event.prev_hash != prev or event.hash != _hash(prev, event.body):
                return False
            prev = event.hash
        return True

    def to_list(self) -> list[dict]:
        """Serialize the chain for persistence."""
        return [
            {"body": e.body, "prev_hash": e.prev_hash, "hash": e.hash}
            for e in self.events
        ]

    @classmethod
    def from_list(cls, events: list[dict]) -> AuditLog:
        """Rebuild a chain from persisted events (call verify() to validate)."""
        log = cls()
        log.events = [
            AuditEvent(body=e["body"], prev_hash=e["prev_hash"], hash=e["hash"])
            for e in events
        ]
        return log
