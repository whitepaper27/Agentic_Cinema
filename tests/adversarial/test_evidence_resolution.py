"""Evidence resolution integrity (sol.md §7 source provenance, §12 gates).

The model may only select a stored source_id and quote a retrieved passage; it can
never supply a citation URL. Code resolves every reference back to a stored source
record, drops unknown IDs and invented quotes, and fills publisher/independence
itself. This is the schema-v2 successor to the E8.1 invariant.
"""

from studioclear.models import Source
from studioclear.research.evidence_normalizer import (
    normalize_quote,
    resolve_assessments,
)


def _sources():
    return [
        Source(
            source_id="S1",
            url="https://www.loc.gov/wright",
            title="Library of Congress — First Flight",
            passages=["The Wright brothers made their first flight in 1903."],
            query="Wright brothers first flight year",
            retrieved_at="2026-09-07T00:00:00Z",
            operation_id="op_1",
        ),
        Source(
            source_id="S2",
            url="https://www.bbc.co.uk/history/flight",
            title="BBC — Aviation history",
            passages=["Powered flight was achieved at Kitty Hawk."],
            query="Wright brothers first flight year",
            retrieved_at="2026-09-07T00:00:00Z",
            operation_id="op_1",
        ),
    ]


def _raw(source_id, quote, relation="supports"):
    return {"source_id": source_id, "relation": relation, "quote": quote,
            "applicable": True, "source_type": "primary"}


def test_unknown_source_id_is_dropped():
    raw = [_raw("S9", "The Wright brothers made their first flight in 1903.")]
    validated, dropped = resolve_assessments(raw, _sources())
    assert validated == []
    assert dropped and dropped[0]["reason"] == "unknown_source_id"


def test_invented_quote_is_dropped():
    raw = [_raw("S1", "The Wright brothers first flew in 1911.")]
    validated, dropped = resolve_assessments(raw, _sources())
    assert validated == []
    assert dropped and dropped[0]["reason"] == "quote_not_grounded"


def test_valid_reference_resolves_publisher_from_stored_source():
    raw = [_raw("S1", "The Wright brothers made their first flight in 1903.")]
    validated, dropped = resolve_assessments(raw, _sources())
    assert dropped == []
    assert len(validated) == 1
    a = validated[0]
    assert a.source_id == "S1"
    # Publisher is derived from the stored URL by code, never trusted from the model.
    assert a.publisher == "loc.gov"


def test_displayed_passage_is_the_retrieved_text_not_model_quote():
    # Model quotes with sloppy whitespace; the stored passage is what we display.
    raw = [_raw("S1", "The   Wright  brothers made their first   flight in 1903.")]
    validated, _ = resolve_assessments(raw, _sources())
    assert validated[0].passage == "The Wright brothers made their first flight in 1903."


def test_model_supplied_url_is_ignored():
    raw = [_raw("S1", "The Wright brothers made their first flight in 1903.")]
    raw[0]["url"] = "https://evil.example/inject"  # model tries to smuggle a citation
    validated, _ = resolve_assessments(raw, _sources())
    # publisher comes from the stored source, not the injected URL
    assert validated[0].publisher == "loc.gov"


def test_normalize_quote_collapses_whitespace_and_case():
    assert normalize_quote("  The  WRIGHT   brothers ") == normalize_quote("the wright brothers")
