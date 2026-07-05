"""Ensure repo-root packages (e.g. `experiments/`) are importable during tests,
independent of pytest version or working directory."""
import os
import sys

_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
