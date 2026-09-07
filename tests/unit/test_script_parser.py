"""Screenplay/scene parsing (sol.md §4, §13.2: plain text + slugs, not only markers)."""

from pathlib import Path

from studioclear.analyzer.script_parser import (
    parse_markdown,
    parse_screenplay_text,
    parse_script,
)

DEMO = Path("demo/demo_script.md")


def test_parses_seven_scenes():
    scenes = parse_script(DEMO)
    assert [s["scene"] for s in scenes] == [1, 2, 3, 4, 5, 6, 7]


def test_plain_text_without_markers_is_one_scene():
    scenes = parse_screenplay_text("A quiet room. She reads a letter about the 1969 landing.")
    assert len(scenes) == 1
    assert scenes[0]["scene"] == 1
    assert "1969 landing" in scenes[0]["text"]


def test_int_ext_slugs_split_into_scenes():
    text = ("INT. KITCHEN - DAY\nShe pours coffee.\n\n"
            "EXT. STREET - NIGHT\nHe waits under a lamppost.")
    scenes = parse_screenplay_text(text)
    assert [s["scene"] for s in scenes] == [1, 2]
    assert "coffee" in scenes[0]["text"]
    assert "lamppost" in scenes[1]["text"]


def test_scene_markers_still_work_via_text_entry():
    scenes = parse_screenplay_text("**SCENE 1 — INT. A**\n\nHello.\n\n**SCENE 2 — EXT. B**\n\nBye.")
    assert [s["scene"] for s in scenes] == [1, 2]


def test_empty_text_is_no_scenes():
    assert parse_screenplay_text("   \n  ") == []


def test_scene_text_is_captured():
    scenes = parse_markdown("**SCENE 1 — INT. A**\n\nHello.\n\n**SCENE 2 — EXT. B**\n\nBye.")
    assert len(scenes) == 2
    assert "Hello." in scenes[0]["text"]
    assert "Bye." in scenes[1]["text"]


def test_unsupported_extension_raises():
    try:
        parse_script("script.docx")
        raise AssertionError("expected ValueError")
    except ValueError:
        pass
