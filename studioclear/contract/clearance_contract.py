"""Load the executable Clearance Contract / studio policy (sol.md §6)."""

from __future__ import annotations

from pathlib import Path

import yaml

DEFAULT_POLICY = Path(__file__).parent / "policy" / "demo_policy_v1.yaml"


def load_policy(path: str | Path = DEFAULT_POLICY) -> dict:
    """Return the `studio_policy` mapping from the contract YAML."""
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return data["clearance_contract"]["studio_policy"]
