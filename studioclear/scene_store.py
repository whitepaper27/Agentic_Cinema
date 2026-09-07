"""Schema-v2 persistence: scenes, versions, and runs (sol.md §9, §10).

One JSON file per scene and per run under DATA_DIR. Every scene is owned by an
opaque session; reads/edits/runs are enforced against that owner so one visitor's
uploads are not exposed to another (sol.md §10). This is a single-session
workspace, not studio identity. GCS-backed durable storage is Phase 5; the file
layout here is the same shape so it ports cleanly.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from studioclear.store import DATA_DIR

SCENES_DIR = DATA_DIR / "scenes"
V2_RUNS_DIR = DATA_DIR / "v2runs"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


def _scene_path(scene_id: str) -> Path:
    return SCENES_DIR / f"{scene_id}.json"


def _run_path(run_id: str) -> Path:
    return V2_RUNS_DIR / f"{run_id}.json"


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
    SCENES_DIR.mkdir(parents=True, exist_ok=True)
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
    _scene_path(scene_id).write_text(json.dumps(scene, indent=2), encoding="utf-8")
    return scene


def get_scene(scene_id: str, owner: str | None = None) -> dict | None:
    p = _scene_path(scene_id)
    if not p.exists():
        return None
    scene = json.loads(p.read_text(encoding="utf-8"))
    if owner is not None and scene.get("owner") != owner:
        raise OwnershipError(scene_id)
    return scene


def save_scene(scene: dict) -> None:
    SCENES_DIR.mkdir(parents=True, exist_ok=True)
    _scene_path(scene["scene_id"]).write_text(json.dumps(scene, indent=2), encoding="utf-8")


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
    V2_RUNS_DIR.mkdir(parents=True, exist_ok=True)
    report["owner"] = owner
    _run_path(report["run_id"]).write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report["run_id"]


def get_run(run_id: str, owner: str | None = None) -> dict | None:
    p = _run_path(run_id)
    if not p.exists():
        return None
    run = json.loads(p.read_text(encoding="utf-8"))
    if owner is not None and run.get("owner") != owner:
        raise OwnershipError(run_id)
    return run
