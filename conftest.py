"""Ensure the repo root is importable no matter how pytest is invoked.

`pytest tests/...` (as CI runs it) does not add the repo root to sys.path the
way `python -m pytest` does, so `import studioclear` fails without this. pytest
auto-loads the rootdir conftest before collection, so this runs first.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
