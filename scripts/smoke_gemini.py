"""Day-1 smoke test (sol.md E1.5 #3): prove Gemini on Vertex AI is reachable.

    python scripts/smoke_gemini.py
"""

from __future__ import annotations


def main() -> None:  # pragma: no cover - manual smoke test
    from google import genai

    # With GOOGLE_GENAI_USE_VERTEXAI=true + ADC, this routes through Vertex AI.
    client = genai.Client()
    resp = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Reply with the single word: ready",
    )
    print("gemini says:", resp.text)


if __name__ == "__main__":
    main()
