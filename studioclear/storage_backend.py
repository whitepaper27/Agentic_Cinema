"""Pluggable storage backend for scenes and runs (sol.md §10).

Local JSON files for development; a private Google Cloud Storage bucket for the
hosted path so runs survive instance restarts and are readable from any instance.
Selection is by environment: set STUDIOCLEAR_GCS_BUCKET to use GCS, otherwise the
local filesystem under STUDIOCLEAR_DATA_DIR is used.

The GCS writer sends a generation precondition (0 for a create, else the object's
current generation) so a concurrent create is not blindly clobbered. Full
read-modify-write compare-and-swap across a mutation is a follow-up; a
single-session workspace rarely mutates one scene from two instances at once.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


class LocalBackend:
    """JSON files under a root directory (development / single instance)."""

    def __init__(self, root: Path):
        self.root = Path(root)

    def read_json(self, key: str) -> Any | None:
        p = self.root / key
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None

    def write_json(self, key: str, obj: Any, custom_time: str | None = None) -> None:
        p = self.root / key
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(obj, indent=2), encoding="utf-8")

    def delete(self, key: str) -> None:
        p = self.root / key
        if p.exists():
            p.unlink()


class GcsBackend:
    """JSON objects in a private GCS bucket, namespaced under a prefix."""

    def __init__(self, bucket_name: str, client: Any | None = None,
                 prefix: str = "studioclear"):
        if client is None:  # pragma: no cover - needs live GCS credentials
            from google.cloud import storage
            client = storage.Client()
        self._bucket = client.bucket(bucket_name)
        self.prefix = prefix.strip("/")

    def _blob(self, key: str):
        return self._bucket.blob(f"{self.prefix}/{key}")

    def read_json(self, key: str) -> Any | None:
        blob = self._blob(key)
        if not blob.exists():
            return None
        return json.loads(blob.download_as_text())

    def write_json(self, key: str, obj: Any, custom_time: str | None = None) -> None:
        blob = self._blob(key)
        existed = blob.exists()
        # Precondition: match the current generation, or 0 to require absence.
        precondition = blob.generation if existed else 0
        # Custom-Time = creation time drives the daysSinceCustomTime lifecycle rule
        # (sol.md §10). Set it only on create so edits/rechecks never extend expiry.
        if not existed and custom_time:
            blob.custom_time = custom_time
        blob.upload_from_string(
            json.dumps(obj, indent=2), content_type="application/json",
            if_generation_match=precondition,
        )

    def delete(self, key: str) -> None:
        blob = self._blob(key)
        if blob.exists():
            blob.delete()


def get_backend():
    """Select the storage backend from the environment (sol.md §10)."""
    bucket = os.getenv("STUDIOCLEAR_GCS_BUCKET")
    if bucket:
        return GcsBackend(bucket)
    from studioclear.store import DATA_DIR
    return LocalBackend(DATA_DIR)
