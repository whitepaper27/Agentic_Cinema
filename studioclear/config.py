"""Runtime configuration (sol.md E1.6).

Loads from environment / .env locally. In Cloud Run, PARALLEL_API_KEY is read
from Secret Manager by the service account — that read is our one real IAM check
(sol.md E3.2 / E8.5), wired in security/secrets.py.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

try:  # optional locally; not required for the pure modules/tests
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # pragma: no cover - dotenv is a convenience only
    pass


def _first_env(*names: str) -> str | None:
    for n in names:
        v = os.getenv(n)
        if v:
            return v
    return None


@dataclass(frozen=True)
class Config:
    gemini_api_key: str | None
    parallel_api_key: str | None
    gcp_project: str | None
    gcp_location: str
    use_vertexai: bool
    extraction_model: str
    normalizer_model: str
    evidence_store: str

    @classmethod
    def from_env(cls) -> Config:
        return cls(
            # Accept the several names a Gemini key might land under.
            gemini_api_key=_first_env(
                "GEMINI_API_KEY", "GOOGLE_API_KEY", "Gemini_API_Key"
            ),
            parallel_api_key=_first_env("PARALLEL_API_KEY", "Parallel_API_Key"),
            gcp_project=os.getenv("GOOGLE_CLOUD_PROJECT"),
            gcp_location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
            # Default to the Gemini Developer API (api-key auth). Set to true only
            # when running against Vertex AI with ADC.
            use_vertexai=os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "false").lower() == "true",
            extraction_model=os.getenv("GEMINI_EXTRACTION_MODEL", "gemini-2.5-pro"),
            normalizer_model=os.getenv("GEMINI_NORMALIZER_MODEL", "gemini-2.5-flash"),
            evidence_store=os.getenv("EVIDENCE_STORE", "json"),
        )
