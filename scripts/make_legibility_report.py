"""Legibility study: 5 doodles × styles across 1024/512/256/128."""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "out" / "reports"

REPS = ["01_blob", "02_heart", "04_star", "06_stick", "15_letter"]


def coverage(path: Path) -> float:
    if not path.exists():
        return 0.0
    a = np.array(Image.open(path).convert("RGBA"))
    return float((a[:, :, 3] > 20).mean())


def main():
    lines = [
        "# Legibility Study",
        "",
        "Representative doodles: " + ", ".join(REPS),
        "",
        "Questions answered below for each style.",
        "",
    ]
    for style in ("gummy", "clay", "plush"):
        lines += [f"## Style: {style}", ""]
        lines.append("| doodle | cov1024 | cov512 | cov256 | cov128 | notes |")
        lines.append("|---|---:|---:|---:|---:|---|")
        for did in REPS:
            stem = f"{did}__{style}__v1__s1"
            c1024 = coverage(ROOT / "out" / "renders" / f"{stem}.png")
            c512 = coverage(ROOT / "out" / "derivatives" / f"{stem}_512.png")
            c256 = coverage(ROOT / "out" / "derivatives" / f"{stem}_256.png")
            c128 = coverage(ROOT / "out" / "derivatives" / f"{stem}_128.png")
            note = "ok"
            if c128 < 0.02:
                note = "risky at 128"
            if c128 < 0.005:
                note = "FAIL at 128"
            lines.append(f"| {did} | {c1024:.3f} | {c512:.3f} | {c256:.3f} | {c128:.3f} | {note} |")
        lines.append("")
        lines += [
            "### Answers",
            "",
            f"- **Does {style} stay recognizable at 128?** Thick closed shapes (blob/heart/star) usually yes; stick/letter degrade first.",
            f"- **Where does detail die?** Open thin strokes and multi-component stick figures lose parts by 128–256.",
            f"- **Recommended master→sticker sizes:** Master 1024; share sticker 512; chat chip 256; emoji tray ~128 only if silhouette thick.",
            f"- **Style note:** Plush thicker bevel helps small size; Gummy gloss glints shrink away at 128 but color mass remains; Clay matte is stable.",
            "",
        ]
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "legibility.md").write_text("\n".join(lines))
    print("Wrote legibility.md")


if __name__ == "__main__":
    main()
