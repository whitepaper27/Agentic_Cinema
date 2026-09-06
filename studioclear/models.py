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
    """The only allowed output states (sol.md §13). No LEGAL/ILLEGAL/SAFE."""

    CLEAR = "CLEAR"
    REVIEW = "REVIEW"
    ESCALATE = "ESCALATE"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    UNRESOLVED = "UNRESOLVED"


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
