"""Build V2 eval contact sheets, V1 vs V2 comparisons, size ladders."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _pil():
    from PIL import Image, ImageDraw, ImageFont
    return Image, ImageDraw, ImageFont


def load_cell(path: Path, cell: int, bg=(255, 255, 255, 255)):
    Image, ImageDraw, _ = _pil()
    slot = Image.new("RGBA", (cell, cell), bg)
    if path.exists():
        im = Image.open(path).convert("RGBA")
        im.thumbnail((cell, cell))
        slot.paste(im, ((cell - im.width) // 2, (cell - im.height) // 2), im)
    else:
        d = ImageDraw.Draw(slot)
        d.line([(0, 0), (cell, cell)], fill=(200, 0, 0, 255), width=2)
        d.line([(cell, 0), (0, cell)], fill=(200, 0, 0, 255), width=2)
    return slot


def comparison_sheet(iter_dir: Path, out_path: Path, styles=("gummy", "clay", "plush", "glossy")):
    Image, ImageDraw, _ = _pil()
    man = json.loads((ROOT / "corpus" / "golden" / "manifest.json").read_text())
    ids = [d["id"] for d in man["doodles"]]
    # columns: doodle preview | V1 gummy (if exists) | V2 styles...
    cols = ["preview", "v1_gummy"] + [f"v2_{s}" for s in styles]
    cell, pad, label_h = 140, 6, 18
    label_w = 120
    W = label_w + len(cols) * (cell + pad) + pad
    H = 40 + len(ids) * (cell + label_h + pad) + pad
    canvas = Image.new("RGBA", (W, H), (245, 245, 248, 255))
    draw = ImageDraw.Draw(canvas)
    draw.text((pad, 8), f"Original → V1 → Best V2 ({iter_dir.name})", fill=(20, 20, 30, 255))
    for c, name in enumerate(cols):
        draw.text((label_w + c * (cell + pad), 22), name[:12], fill=(0, 0, 0, 255))
    for r, did in enumerate(ids):
        y = 40 + r * (cell + label_h + pad)
        draw.text((pad, y + cell // 2 - 6), did, fill=(20, 20, 30, 255))
        paths = [
            ROOT / "corpus" / "golden" / f"{did}_preview.png",
            ROOT / "out" / "renders" / f"{did.replace(did[:2], did[:2])}__gummy__v1__s1.png",
        ]
        # map golden ids to nearest v1 corpus where possible
        v1_map = {
            "01_blob": "01_blob",
            "02_heart": "02_heart",
            "03_star": "04_star",
            "04_face": "05_face",
            "05_plant": "09_flower",
            "08_flower": "09_flower",
            "10_open_stroke": "10_open",
            "11_multi_part": "12_multi",
            "12_messy_incomplete": "19_messy",
        }
        v1_id = v1_map.get(did, did)
        paths[1] = ROOT / "out" / "renders" / f"{v1_id}__gummy__v1__s1.png"
        for c, style in enumerate(styles):
            paths.append(iter_dir / "renders" / f"{did}__{style}__v2__s1.png")
        for c, p in enumerate([paths[0], paths[1]] + paths[2:]):
            x = label_w + c * (cell + pad)
            canvas.paste(load_cell(p, cell), (x, y))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path)
    return out_path


def size_ladder(iter_dir: Path, out_path: Path, doodle_id="02_heart", style="gummy"):
    Image, ImageDraw, _ = _pil()
    stem = f"{doodle_id}__{style}__v2__s1"
    master = iter_dir / "renders" / f"{stem}.png"
    sizes = [1024, 512, 256, 128]
    cell_pad = 12
    # place each size naturally
    W = sum(sizes) + cell_pad * (len(sizes) + 1)
    H = max(sizes) + 50
    canvas = Image.new("RGBA", (W, H), (245, 245, 248, 255))
    draw = ImageDraw.Draw(canvas)
    draw.text((cell_pad, 8), f"Size ladder {doodle_id} × {style}.v2", fill=(20, 20, 30, 255))
    x = cell_pad
    if master.exists():
        im = Image.open(master).convert("RGBA")
        for s in sizes:
            d = im.copy()
            d.thumbnail((s, s))
            slot = Image.new("RGBA", (s, s), (255, 255, 255, 255))
            slot.paste(d, ((s - d.width) // 2, (s - d.height) // 2), d)
            canvas.paste(slot, (x, 36))
            draw.text((x, 36 + s + 2), str(s), fill=(0, 0, 0, 255))
            x += s + cell_pad
    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path)
    return out_path


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--iter", type=int, default=1)
    args = ap.parse_args()
    iter_dir = ROOT / "out" / "v2" / f"iter_{args.iter:02d}"
    cs = iter_dir / "contact_sheets"
    comparison_sheet(iter_dir, cs / "compare_v1_v2.png")
    for style in ("gummy", "clay", "plush", "glossy"):
        size_ladder(iter_dir, cs / f"size_ladder_{style}.png", "02_heart", style)
        size_ladder(iter_dir, cs / f"size_ladder_star_{style}.png", "03_star", style)
    print("eval sheets written to", cs)


if __name__ == "__main__":
    main()
