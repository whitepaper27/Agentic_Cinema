"""Signal Room repair gate (sol.md §12 / §13.1).

Reproduces the observed failure BEFORE repair: a claim added only to the canonical
scene text must appear in recheck coverage. The old recheck reused the saved item
list and never re-extracted, so an added claim was silently unchecked while recheck
reported 'complete'. Uses a text-aware stub provider (not the fixed fixture) so the
control flow is exercised honestly.
"""

import re

from studioclear import revision
from studioclear.models import ClearanceItem, ItemType
from studioclear.providers.base import Providers
from studioclear.research_pipeline import run_research

SIGNAL_ROOM = (
    "INT. SIGNAL ROOM - NIGHT\nSUPER: 1935\n\n"
    "ELSIE\nKeep the light on. I promised I would return.\n\n"
    "She photographs the logbook with a digital camera.\n"
    "An unidentified crest is stamped on the door."
)
CABLE = "A caption says: The first transatlantic cable opened in 1858."

_YEAR = re.compile(r"\b(1[6-9]\d\d|20\d\d)\b")


class _TextAwareLLM:
    """Extracts a claim from any sentence mentioning a camera or a year."""

    def extract_items(self, scenes):
        items, i = [], 0
        for sc in scenes:
            for sent in re.split(r"(?<=[.!?])\s+|\n+", sc.get("text", "")):
                s = sent.strip()
                if len(s) < 6:
                    continue
                if "camera" in s.lower() or _YEAR.search(s):
                    i += 1
                    items.append(ClearanceItem(
                        item_id=f"CLR-{i:03d}", scene=sc.get("scene", 1),
                        type=ItemType.HISTORICAL_CLAIM, text_span=s))
        return items

    def extract_items_from_images(self, images):
        return []

    def assess_claim(self, claim, sources):
        return []                       # no evidence here → UNRESOLVED, but researched

    def propose_revision(self, scene_text, claim, evidence, instruction, locks):
        return {"original_text": claim, "proposed_text": claim, "rationale": "",
                "evidence_source_ids": [], "art_change": ""}


class _EmptySearch:
    def search(self, query, item):
        return []


def _providers():
    return Providers(llm=_TextAwareLLM(), search=_EmptySearch())


def _scene_with(text, items):
    return {
        "scene_id": "scene_sig", "owner": "o", "current_version": 1,
        "title": "Signal Room", "instruction": "Check the props fit the year.",
        "run_ids": [],
        "versions": [{"version": 1, "parent_version": None,
                      "scenes": [{"scene": 1, "text": text}],
                      "items": [it.model_dump(mode="json") for it in items],
                      "instruction": "", "locks": []}],
    }


def test_added_claim_appears_in_recheck_coverage():
    providers = _providers()
    items = providers.llm.extract_items([{"scene": 1, "text": SIGNAL_ROOM}])
    scene = _scene_with(SIGNAL_ROOM, items)
    prior = run_research(items, providers, run_id="sig_r1")

    # A later controlled edit appends a NEW researchable claim to the canonical text.
    v2_text = SIGNAL_ROOM + "\n" + CABLE
    scene["versions"].append({"version": 2, "parent_version": 1,
                              "scenes": [{"scene": 1, "text": v2_text}],
                              "items": scene["versions"][0]["items"],  # NOT re-extracted on save
                              "instruction": "", "locks": []})
    scene["current_version"] = 2

    new_run = revision.recheck(scene, providers, prior, run_id="sig_r2")
    covered = " ".join(f["text_span"].lower() for f in new_run["findings"])
    # The added cable claim must be extracted and researched during recheck.
    assert "cable" in covered
    assert "CLR" in " ".join(new_run["recheck"]["added"]) or new_run["recheck"]["added"]
