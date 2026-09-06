"""Script -> text per scene (sol.md E3.1.1).

parse_script dispatches on extension: Markdown (the demo fixture) is parsed for
real and offline; PDF via pypdf is the live-build path.
"""

from __future__ import annotations

import re
from pathlib import Path

_SCENE_RE = re.compile(r"^\*\*SCENE\s+(\d+)", re.IGNORECASE | re.MULTILINE)


def parse_markdown(text: str) -> list[dict]:
    """Split a Markdown screenplay into scenes on `**SCENE N ...` headings.
    Returns [{"scene": int, "text": str}, ...] in order."""
    matches = list(_SCENE_RE.finditer(text))
    scenes: list[dict] = []
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        scenes.append({"scene": int(m.group(1)), "text": text[start:end].strip()})
    return scenes


def parse_script(path: str | Path) -> list[dict]:
    p = Path(path)
    if p.suffix.lower() == ".md":
        return parse_markdown(p.read_text(encoding="utf-8"))
    if p.suffix.lower() == ".pdf":  # pragma: no cover - live build
        raise NotImplementedError(
            "Wire pypdf on the live build: extract text, split on INT./EXT. slugs."
        )
    raise ValueError(f"unsupported script type: {p.suffix}")
