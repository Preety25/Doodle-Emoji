#!/usr/bin/env python3
"""CLI entry: python3 scripts/v4_v43_multi_style_transform.py → lab.v4.v43_multi_style_transform."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lab.v4.v43_multi_style_transform import main

if __name__ == "__main__":
    raise SystemExit(main())
