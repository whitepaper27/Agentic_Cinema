"""Schema-v2 persistence: scenes, versions, and runs (sol.md §9, §10).

One JSON object per scene and per run, stored through a pluggable backend: local
files for dev, a private GCS bucket for the hosted path (set STUDIOCLEAR_GCS_BUCKET).
Every scene is owned by an opaque session; reads/edits/runs are enforced against
that owner so one visitor's uploads are not exposed to another (sol.md §10). This
is a single-session workspace, not studio identity.
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone

from studioclear.storage_backend import GcsBackend, LocalBackend
from studioclear.store import DATA_DIR

_gcs_backend = None


def _backend():
    """Durable GCS bucket when configured, else local files (sol.md §10)."""
    global _gcs_backend
    bucket = os.getenv("STUDIOCLEAR_GCS_BUCKET")
    if bucket:
        if _gcs_backend is None:
            _gcs_backend = GcsBackend(bucket)
        return _gcs_backend
    return LocalBackend(DATA_DIR)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


def _scene_key(scene_id: str) -> str:
    return f"scenes/{scene_id}.json"


def _run_key(run_id: str) -> str:
    return f"v2runs/{run_id}.json"


class OwnershipError(PermissionError):
    """Raised when a session tries to touch a scene/run it does not own."""


def create_scene(
    owner: str,
    *,
    source_type: str,
    title: str,
    instruction: str,
    draft_scenes: list[dict],
    items: list[dict],
    provider_mode: str,
    locks: list[str] | None = None,
) -> dict:
    """Persist a new scene at version 1 with its editable extraction draft."""
    scene_id = new_id("scene")
    scene = {
        "scene_id": scene_id,
        "owner": owner,
        "source_type": source_type,          # "paste" | "images"
        "title": title or "Untitled scene",
        "provider_mode": provider_mode,       # "live" | "example"
        "instruction": instruction,
        "locks": locks or [],
        "current_version": 1,
        "created_at": _now(),
        "versions": [{
            "version": 1,
            "parent_version": None,
            "created_at": _now(),
            "scenes": draft_scenes,           # [{scene, text, ...}] editable transcript
            "items": items,                   # extracted candidate claims (editable)
            "instruction": instruction,
            "locks": locks or [],
        }],
    }
    _backend().write_json(_scene_key(scene_id), scene)
    return scene


def get_scene(scene_id: str, owner: str | None = None) -> dict | None:
    scene = _backend().read_json(_scene_key(scene_id))
    if scene is None:
        return None
    if owner is not None and scene.get("owner") != owner:
        raise OwnershipError(scene_id)
    return scene


def save_scene(scene: dict) -> None:
    _backend().write_json(_scene_key(scene["scene_id"]), scene)


def latest_version(scene: dict) -> dict:
    return scene["versions"][-1]


def update_scene_version(
    scene: dict,
    *,
    expected_version: int,
    scenes: list[dict] | None = None,
    items: list[dict] | None = None,
    instruction: str | None = None,
    locks: list[str] | None = None,
) -> dict:
    """Create a new immutable scene version from a correction (sol.md §5, §8).

    Requires the caller's expected version to match current (optimistic
    concurrency); raises ValueError on a stale write so the API can return 409.
    """
    current = scene["current_version"]
    if expected_version != current:
        raise ValueError(f"stale_version: expected {current}, got {expected_version}")
    base = latest_version(scene)
    new_version = current + 1
    version = {
        "version": new_version,
        "parent_version": current,
        "created_at": _now(),
        "scenes": scenes if scenes is not None else base["scenes"],
        "items": items if items is not None else base["items"],
        "instruction": instruction if instruction is not None else base["instruction"],
        "locks": locks if locks is not None else base["locks"],
    }
    scene["versions"].append(version)
    scene["current_version"] = new_version
    if instruction is not None:
        scene["instruction"] = instruction
    if locks is not None:
        scene["locks"] = locks
    save_scene(scene)
    return version


def save_run(report: dict, owner: str) -> str:
    report["owner"] = owner
    _backend().write_json(_run_key(report["run_id"]), report)
    return report["run_id"]


def get_run(run_id: str, owner: str | None = None) -> dict | None:
    run = _backend().read_json(_run_key(run_id))
    if run is None:
        return None
    if owner is not None and run.get("owner") != owner:
        raise OwnershipError(run_id)
    return run
