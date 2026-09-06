"""Evidence store (sol.md §11).

Reusable evidence with a freshness check — but no complex semantic-memory
platform this week. P0 = JSON file or Firestore. Stub interface below.
"""

from __future__ import annotations

from studioclear.models import EvidenceRecord


class EvidenceStore:  # pragma: no cover - stub
    """STUB. Implement with Firestore (collection `evidence`) or a JSON file.
    lookup() should return a cached record if fresh, else None (sol.md §11)."""

    def lookup(self, item_id: str) -> EvidenceRecord | None:
        raise NotImplementedError

    def save(self, record: EvidenceRecord) -> None:
        raise NotImplementedError
