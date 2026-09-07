"""Script -> text per scene (sol.md E3.1.1).

parse_script dispatches on extension: Markdown (the demo fixture) is parsed for
real and offline; PDF via pypdf is the live-build path.
"""

from __future__ import annotations

import re
from pathlib import Path

_SCENE_RE = re.compile(r"^\*\*SCENE\s+(\d+)", re.IGNORECASE | re.MULTILINE)
# Standard screenplay scene headings (slug lines).
_SLUG_RE = re.compile(r"^\s*(INT\.|EXT\.|INT/EXT\.|I/E\.)", re.IGNORECASE | re.MULTILINE)


def _split_on(pattern: re.Pattern[str], text: str) -> list[dict]:
    matches = list(pattern.finditer(text))
    scenes: list[dict] = []
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        scenes.append({"scene": i + 1, "text": text[start:end].strip()})
    return scenes


def parse_markdown(text: str) -> list[dict]:
    """Split a Markdown screenplay into scenes on `**SCENE N ...` headings,
    preserving the authored scene numbers."""
    matches = list(_SCENE_RE.finditer(text))
    scenes: list[dict] = []
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        scenes.append({"scene": int(m.group(1)), "text": text[start:end].strip()})
    return scenes


def parse_screenplay_text(text: str) -> list[dict]:
    """Parse arbitrary pasted scene text (sol.md §13.2).

    Tolerant of ordinary material: `**SCENE N` markers if present, else INT./EXT.
    slug lines, else the whole thing as a single scene. Empty/whitespace input
    yields no scenes so the caller can reject it honestly."""
    if not (text or "").strip():
        return []
    if _SCENE_RE.search(text):
        return parse_markdown(text)
    if _SLUG_RE.search(text):
        return _split_on(_SLUG_RE, text)
    return [{"scene": 1, "text": text.strip()}]


def parse_script(path: str | Path) -> list[dict]:
    p = Path(path)
    if p.suffix.lower() in (".md", ".txt"):
        return parse_screenplay_text(p.read_text(encoding="utf-8"))
    if p.suffix.lower() == ".pdf":  # pragma: no cover - deferred (sol.md §4)
        raise NotImplementedError("PDF import is deferred until after submission (sol.md §4).")
    raise ValueError(f"unsupported script type: {p.suffix}")
