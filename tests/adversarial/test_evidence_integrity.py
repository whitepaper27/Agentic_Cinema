"""Evidence-integrity invariant (sol.md E8.1 / E3.1.5): the model can never
introduce a citation. Any URL not in the raw Parallel response is dropped."""

from studioclear.research.evidence_normalizer import (
    enforce_grounded_sources,
    independent_source_count,
)

# The only URLs that provably came back from the Parallel API for this item.
PARALLEL_URLS = [
    "https://www.nasa.gov/apollo-11",
    "https://en.wikipedia.org/wiki/Apollo_11",
]


def test_invented_url_is_dropped():
    candidates = PARALLEL_URLS + ["https://totally-made-up-source.example/fabricated"]
    grounded, dropped = enforce_grounded_sources(candidates, PARALLEL_URLS)
    assert grounded == PARALLEL_URLS
    assert dropped == ["https://totally-made-up-source.example/fabricated"]


def test_all_grounded_when_faithful():
    grounded, dropped = enforce_grounded_sources(PARALLEL_URLS, PARALLEL_URLS)
    assert grounded == PARALLEL_URLS and dropped == []


def test_source_independence_counts_distinct_publishers():
    # Same story syndicated under two URLs on one domain counts once.
    urls = [
        "https://news.example.com/a",
        "https://news.example.com/a-copy",
        "https://other.org/b",
    ]
    assert independent_source_count(urls) == 2
