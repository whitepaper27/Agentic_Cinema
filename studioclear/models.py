"""Shared data contracts (pydantic v2).

These schemas are the spine of the pipeline (sol.md §5, §10, §13, §16, §19).
Everything downstream depends on them being deterministic and validated, so
they are real and tested from day one — not stubs.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, HttpUrl


class ItemType(str, Enum):
    BRAND = "brand"
    LIVING_PERSON = "living_person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    SONG = "song"
    HISTORICAL_CLAIM = "historical_claim"
    MEDICAL_CLAIM = "medical_claim"
    FICTIONAL_BRAND = "fictional_brand"


class ClearanceState(str, Enum):
    """LEGACY triage states (schema v1). Retained only to read/label old saved
    runs (sol.md §7 Compatibility). New runs use ResearchStatus + Routing."""

    CLEAR = "CLEAR"
    REVIEW = "REVIEW"
    ESCALATE = "ESCALATE"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    UNRESOLVED = "UNRESOLVED"


class ResearchStatus(str, Enum):
    """What the retrieved evidence says about a claim (sol.md §7). This is a
    research finding, NOT a legal/clearance verdict and NOT a human decision."""

    SUPPORTED = "SUPPORTED"          # applicable evidence meets the studio research policy
    CONTRADICTED = "CONTRADICTED"    # applicable evidence directly challenges the claim
    MIXED = "MIXED"                  # material support and contradiction, unresolved
    UNRESOLVED = "UNRESOLVED"        # evidence/context/quality/applicability insufficient
    NOT_RESEARCHED = "NOT_RESEARCHED"  # out of scope or skipped by a recorded budget
    STALE = "STALE"                  # belongs to an older scene version; awaits recheck


class Routing(str, Enum):
    """Human-review routing, kept separate from research status (sol.md §7).
    A factually SUPPORTED scene may still need rights/producer review."""

    NONE = "NONE"
    REVIEW = "REVIEW"
    ESCALATE = "ESCALATE"


class Relation(str, Enum):
    """How one retrieved passage bears on a specific claim (sol.md §7)."""

    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    CONTEXT_ONLY = "context_only"
    UNCLEAR = "unclear"


class SourceType(str, Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    UNKNOWN = "unknown"


class Source(BaseModel):
    """A raw retrieved source with a server-assigned immutable id (sol.md §7).

    Passages are the exact retrieved text; a displayed quote must match one of
    them. The model may reference `source_id` but never supplies `url`."""

    source_id: str
    url: str
    title: str = ""
    passages: list[str] = Field(default_factory=list)
    query: str = ""
    retrieved_at: str = ""
    operation_id: str = ""
    publisher: str = ""
    independence: str = "unknown"      # "documented" | "unknown"


class ClaimAssessment(BaseModel):
    """A validated source/claim assessment (sol.md §7 claim-assessment table).

    The model selects a stored `source_id` and passage; it never supplies a URL.
    `publisher`/`independence` are resolved from the stored Source by code, not
    the model, and drive the deterministic corroboration rule."""

    source_id: str
    relation: Relation
    applicable: bool = False           # directly applicable to entity/date/place/scope
    source_type: SourceType = SourceType.UNKNOWN
    publisher: str = ""
    independence: str = "unknown"      # "documented" | "unknown"
    passage: str = ""                  # exact retrieved text, matched to the source
    explanation: str = ""              # may paraphrase; never a substitute for the passage
    limitations: str = ""


class ClearanceItem(BaseModel):
    """A normalized clearance item extracted from the script (sol.md §5)."""

    item_id: str = Field(..., examples=["CLR-007"])
    scene: int
    type: ItemType
    text_span: str
    context: str = ""
    research_required: bool = True
    state: ClearanceState = ClearanceState.UNRESOLVED


class EvidenceItem(BaseModel):
    """A single cited source. `source_url` MUST come from Parallel, never an LLM
    (sol.md E3.1.5 / E8.1 — the evidence-integrity invariant)."""

    source_url: HttpUrl
    title: str = ""
    excerpt: str = ""
    retrieved_at: str = ""  # ISO-8601, passed through from the Parallel response
    supports: bool = True
    publisher: str = ""  # host/domain, used for the source-independence check (E5.7)


class EvidenceRecord(BaseModel):
    """All evidence for one clearance item (sol.md §10)."""

    item_id: str
    query: str
    evidence: list[EvidenceItem] = Field(default_factory=list)
    source_count: int = 0
    confidence: float = 0.0
    freshness: str = "current"


class ExecutionContext(BaseModel):
    """Context carried on every sensitive action (sol.md §16)."""

    subject_id: str
    script_id: str
    agent_id: str
    run_id: str
    tool: str
    action: str
    permissions: list[str] = Field(default_factory=list)
    risk_tier: str = "research"


class Decision(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
