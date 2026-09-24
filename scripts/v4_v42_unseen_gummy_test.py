#!/usr/bin/env python3
"""CLI entry: python3 scripts/v4_v42_unseen_gummy_test.py → lab.v4.v42_unseen_gummy_test."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lab.v4.v42_unseen_gummy_test import main

if __name__ == "__main__":
    raise SystemExit(main())
