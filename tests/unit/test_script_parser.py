"""Markdown screenplay parsing (sol.md E3.1.1)."""

from pathlib import Path

from studioclear.analyzer.script_parser import parse_markdown, parse_script

DEMO = Path("demo/demo_script.md")


def test_parses_seven_scenes():
    scenes = parse_script(DEMO)
    assert [s["scene"] for s in scenes] == [1, 2, 3, 4, 5, 6, 7]


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
