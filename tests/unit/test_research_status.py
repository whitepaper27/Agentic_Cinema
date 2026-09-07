"""Deterministic research-status mapping (sol.md §7).

Code maps validated structured claim assessments to a single research status.
The evidence foundation gate (sol.md §13.1): irrelevant or contradicting sources
can never clear a factual claim.
"""

from studioclear.contract.policy_evaluator import assess_research_status
from studioclear.models import ClaimAssessment, Relation, ResearchStatus, SourceType

FACTUAL_POLICY = {"factual": {"minimum_corroborating_sources": 2}}


def _a(relation, *, applicable=True, source_type=SourceType.SECONDARY,
       publisher="example.com", independence="unknown"):
    return ClaimAssessment(
        source_id="S1", relation=relation, applicable=applicable,
        source_type=source_type, publisher=publisher, independence=independence,
    )


def test_no_assessments_is_unresolved():
    assert assess_research_status([], FACTUAL_POLICY) is ResearchStatus.UNRESOLVED


def test_context_only_source_is_unresolved_not_supported():
    # A passage that merely mentions the subject without supporting the claim.
    assessments = [_a(Relation.CONTEXT_ONLY)]
    assert assess_research_status(assessments, FACTUAL_POLICY) is ResearchStatus.UNRESOLVED


def test_unclear_relation_is_unresolved():
    got = assess_research_status([_a(Relation.UNCLEAR)], FACTUAL_POLICY)
    assert got is ResearchStatus.UNRESOLVED


def test_single_applicable_primary_support_is_supported():
    # One directly applicable primary source meets the factual threshold.
    a = _a(Relation.SUPPORTS, source_type=SourceType.PRIMARY, publisher="loc.gov")
    assert assess_research_status([a], FACTUAL_POLICY) is ResearchStatus.SUPPORTED


def test_two_documented_independent_secondary_supports_is_supported():
    aa = [
        _a(Relation.SUPPORTS, publisher="nytimes.com", independence="documented"),
        _a(Relation.SUPPORTS, publisher="bbc.co.uk", independence="documented"),
    ]
    assert assess_research_status(aa, FACTUAL_POLICY) is ResearchStatus.SUPPORTED


def test_two_supports_same_publisher_is_not_corroboration():
    # Same publisher twice is a syndication artifact, not independent corroboration.
    aa = [
        _a(Relation.SUPPORTS, publisher="nytimes.com", independence="documented"),
        _a(Relation.SUPPORTS, publisher="nytimes.com", independence="documented"),
    ]
    assert assess_research_status(aa, FACTUAL_POLICY) is ResearchStatus.UNRESOLVED


def test_two_supports_independence_unknown_is_not_corroboration():
    aa = [
        _a(Relation.SUPPORTS, publisher="a.com", independence="unknown"),
        _a(Relation.SUPPORTS, publisher="b.com", independence="unknown"),
    ]
    assert assess_research_status(aa, FACTUAL_POLICY) is ResearchStatus.UNRESOLVED


def test_non_applicable_support_does_not_count():
    # Supports the claim but about the wrong entity/date/place → not applicable.
    a = _a(Relation.SUPPORTS, source_type=SourceType.PRIMARY, applicable=False)
    assert assess_research_status([a], FACTUAL_POLICY) is ResearchStatus.UNRESOLVED


def test_single_applicable_contradiction_is_contradicted():
    a = _a(Relation.CONTRADICTS, source_type=SourceType.PRIMARY, publisher="loc.gov")
    assert assess_research_status([a], FACTUAL_POLICY) is ResearchStatus.CONTRADICTED


def test_support_meeting_bar_plus_contradiction_is_mixed():
    aa = [
        _a(Relation.SUPPORTS, source_type=SourceType.PRIMARY, publisher="loc.gov"),
        _a(Relation.CONTRADICTS, source_type=SourceType.PRIMARY, publisher="archives.gov"),
    ]
    assert assess_research_status(aa, FACTUAL_POLICY) is ResearchStatus.MIXED


def test_weak_support_plus_contradiction_is_contradicted():
    # Support present but below the bar; an applicable contradiction stands.
    aa = [
        _a(Relation.SUPPORTS, publisher="blog.example", independence="unknown"),
        _a(Relation.CONTRADICTS, source_type=SourceType.PRIMARY, publisher="loc.gov"),
    ]
    assert assess_research_status(aa, FACTUAL_POLICY) is ResearchStatus.CONTRADICTED
