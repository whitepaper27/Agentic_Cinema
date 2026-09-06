"""StudioClear — Agentic Script Clearance Research Desk.

Package layout maps to sol.md §26 / E3.0:
  analyzer/  contract/  agents/  research/  security/  evals/

The pure, load-bearing modules (models, policy evaluator, security, evidence
integrity, deterministic confidence) are implemented and unit-tested. The
external-API surfaces (Gemini extraction, Parallel search, ADK agents,
Firestore) are clean stubs to fill in on the 4-day build.
"""

__version__ = "0.1.0"
