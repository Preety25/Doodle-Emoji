"""Build V2 eval contact sheets, V1 vs V2 comparisons, size ladders, style grids."""
from __future__ import annotations

import json
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
    v1_root = ROOT / "out" / "v2" / "v1_baseline" / "renders"
    legacy_v1 = ROOT / "out" / "renders"
    for r, did in enumerate(ids):
        y = 40 + r * (cell + label_h + pad)
        draw.text((pad, y + cell // 2 - 6), did, fill=(20, 20, 30, 255))
        preview = ROOT / "corpus" / "golden" / f"{did}_preview.png"
        v1 = v1_root / f"{did}__gummy__v1__s1.png"
        if not v1.exists():
            v1 = legacy_v1 / f"{did}__gummy__v1__s1.png"
        paths = [preview, v1] + [iter_dir / "renders" / f"{did}__{style}__v2__s1.png" for style in styles]
        for c, path in enumerate(paths):
            x = label_w + c * (cell + pad)
            canvas.paste(load_cell(path, cell), (x, y))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path)
    return out_path


def style_trio_sheet(iter_dir: Path, out_path: Path, styles=("gummy", "clay", "plush")):
    """Gummy / Clay / Plush hero comparison across golden-12."""
    Image, ImageDraw, _ = _pil()
    man = json.loads((ROOT / "corpus" / "golden" / "manifest.json").read_text())
    ids = [d["id"] for d in man["doodles"]]
    cell, pad, label_h = 150, 8, 18
    label_w = 120
    W = label_w + len(styles) * (cell + pad) + pad
    H = 40 + len(ids) * (cell + label_h + pad) + pad
    canvas = Image.new("RGBA", (W, H), (245, 245, 248, 255))
    draw = ImageDraw.Draw(canvas)
    draw.text((pad, 8), f"Gummy / Clay / Plush — {iter_dir.name}", fill=(20, 20, 30, 255))
    for c, s in enumerate(styles):
        draw.text((label_w + c * (cell + pad), 22), s, fill=(0, 0, 0, 255))
    for r, did in enumerate(ids):
        y = 40 + r * (cell + label_h + pad)
        draw.text((pad, y + cell // 2 - 6), did, fill=(20, 20, 30, 255))
        for c, style in enumerate(styles):
            x = label_w + c * (cell + pad)
            p = iter_dir / "renders" / f"{did}__{style}__v2__s1.png"
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


def best_contact(iter_dir: Path, out_path: Path, styles=("gummy", "clay", "plush", "glossy")):
    """Compact BEST contact: all doodles × styles."""
    Image, ImageDraw, _ = _pil()
    man = json.loads((ROOT / "corpus" / "golden" / "manifest.json").read_text())
    ids = [d["id"] for d in man["doodles"]]
    cell, pad = 110, 6
    label_w = 110
    W = label_w + len(styles) * (cell + pad) + pad
    H = 36 + len(ids) * (cell + pad) + pad
    canvas = Image.new("RGBA", (W, H), (245, 245, 248, 255))
    draw = ImageDraw.Draw(canvas)
    draw.text((pad, 8), f"BEST-V2 contact — {iter_dir.name}", fill=(20, 20, 30, 255))
    for c, s in enumerate(styles):
        draw.text((label_w + c * (cell + pad), 20), s, fill=(0, 0, 0, 255))
    for r, did in enumerate(ids):
        y = 36 + r * (cell + pad)
        draw.text((pad, y + cell // 2 - 6), did, fill=(20, 20, 30, 255))
        for c, style in enumerate(styles):
            x = label_w + c * (cell + pad)
            canvas.paste(load_cell(iter_dir / "renders" / f"{did}__{style}__v2__s1.png", cell), (x, y))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path)
    return out_path


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--iter", type=int, default=1)
    ap.add_argument("--comparisons-dir", default="")
    args = ap.parse_args()
    iter_dir = ROOT / "out" / "v2" / f"iter_{args.iter:02d}"
    cs = iter_dir / "contact_sheets"
    cmp = Path(args.comparisons_dir) if args.comparisons_dir else (ROOT / "out" / "v2" / "comparisons")
    cmp.mkdir(parents=True, exist_ok=True)
    comparison_sheet(iter_dir, cs / "compare_original_v1_v2.png")
    comparison_sheet(iter_dir, cmp / "original_v1_v2.png")
    style_trio_sheet(iter_dir, cs / "gummy_clay_plush.png")
    style_trio_sheet(iter_dir, cmp / "gummy_clay_plush.png")
    best_contact(iter_dir, cs / "best_contact.png")
    best_contact(iter_dir, cmp / "best_v2_contact.png")
    for style in ("gummy", "clay", "plush", "glossy"):
        size_ladder(iter_dir, cs / f"size_ladder_{style}.png", "02_heart", style)
        size_ladder(iter_dir, cmp / f"size_ladder_heart_{style}.png", "02_heart", style)
        size_ladder(iter_dir, cs / f"size_ladder_star_{style}.png", "03_star", style)
    # also copy per-style contacts if benchmark created them
    print("eval sheets written to", cs, "and", cmp)


if __name__ == "__main__":
    main()
