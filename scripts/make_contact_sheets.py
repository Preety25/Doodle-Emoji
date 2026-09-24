"""Build contact sheets from rendered PNGs."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RENDERS = ROOT / "out" / "renders"
OUT = ROOT / "out" / "contact_sheets"
STYLES = ["gummy", "clay", "plush"]


def _pil():
    from PIL import Image, ImageDraw, ImageFont
    return Image, ImageDraw, ImageFont


def sheet_for_style(style_id: str, cell=256, cols=5):
    Image, ImageDraw, ImageFont = _pil()
    man = json.loads((ROOT / "corpus" / "manifest.json").read_text())
    ids = [d["id"] for d in man["doodles"]]
    rows = (len(ids) + cols - 1) // cols
    pad = 8
    label_h = 22
    W = cols * cell + (cols + 1) * pad
    H = rows * (cell + label_h) + (rows + 1) * pad + 40
    canvas = Image.new("RGBA", (W, H), (245, 245, 248, 255))
    draw = ImageDraw.Draw(canvas)
    draw.text((pad, 10), f"Style: {style_id}.v1  (20 doodles)", fill=(30, 30, 40, 255))
    for i, did in enumerate(ids):
        r, c = divmod(i, cols)
        x = pad + c * (cell + pad)
        y = 40 + pad + r * (cell + label_h + pad)
        stem = f"{did}__{style_id}__v1__s1.png"
        p = RENDERS / stem
        if p.exists():
            im = Image.open(p).convert("RGBA")
            im.thumbnail((cell, cell))
            bg = Image.new("RGBA", (cell, cell), (255, 255, 255, 255))
            ox = (cell - im.width) // 2
            oy = (cell - im.height) // 2
            bg.paste(im, (ox, oy), im)
            canvas.paste(bg, (x, y))
        else:
            draw.rectangle([x, y, x + cell, y + cell], outline=(200, 80, 80), width=2)
            draw.text((x + 8, y + cell // 2), "FAIL", fill=(200, 80, 80, 255))
        draw.text((x, y + cell + 2), did, fill=(40, 40, 50, 255))
    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / f"contact_{style_id}.png"
    canvas.save(out)
    return out


def sheet_all_styles(thumb=128):
    Image, ImageDraw, ImageFont = _pil()
    man = json.loads((ROOT / "corpus" / "manifest.json").read_text())
    ids = [d["id"] for d in man["doodles"]]
    cols = 1 + len(STYLES)
    rows = len(ids)
    pad = 6
    cell = thumb
    label_w = 110
    W = label_w + cols * cell + (cols + 1) * pad
    H = 40 + rows * (cell + pad) + pad
    canvas = Image.new("RGBA", (W, H), (245, 245, 248, 255))
    draw = ImageDraw.Draw(canvas)
    draw.text((pad, 10), "All styles grid (rows=doodles, cols=styles)", fill=(30, 30, 40, 255))
    headers = ["id"] + STYLES
    for c, h in enumerate(headers):
        x = (label_w if c else pad) + (0 if c == 0 else (c - 1) * (cell + pad) + label_w + pad)
        if c == 0:
            draw.text((pad, 28), h, fill=(0, 0, 0, 255))
        else:
            draw.text((label_w + pad + (c - 1) * (cell + pad), 28), h, fill=(0, 0, 0, 255))
    for r, did in enumerate(ids):
        y = 40 + r * (cell + pad)
        draw.text((pad, y + cell // 2 - 6), did, fill=(20, 20, 30, 255))
        for c, style in enumerate(STYLES):
            x = label_w + pad + c * (cell + pad)
            p = RENDERS / f"{did}__{style}__v1__s1.png"
            slot = Image.new("RGBA", (cell, cell), (255, 255, 255, 255))
            if p.exists():
                im = Image.open(p).convert("RGBA")
                im.thumbnail((cell, cell))
                ox = (cell - im.width) // 2
                oy = (cell - im.height) // 2
                slot.paste(im, (ox, oy), im)
            else:
                d = ImageDraw.Draw(slot)
                d.line([(0, 0), (cell, cell)], fill=(200, 0, 0, 255), width=2)
            canvas.paste(slot, (x, y))
    out = OUT / "contact_all_styles.png"
    OUT.mkdir(parents=True, exist_ok=True)
    canvas.save(out)
    return out


def sheet_failures():
    Image, ImageDraw, ImageFont = _pil()
    fails = []
    for p in sorted(RENDERS.glob("*.json")):
        try:
            m = json.loads(p.read_text())
            if not m.get("success"):
                fails.append(m)
        except Exception:
            pass
    OUT.mkdir(parents=True, exist_ok=True)
    if not fails:
        (OUT / "failures.txt").write_text("No failures logged.\n")
        return None
    lines = [f"{m.get('doodle_id')}__{m.get('style_id')}: {str(m.get('error'))[:180]}" for m in fails]
    (OUT / "failures.txt").write_text("\n".join(lines) + "\n")
    return OUT / "failures.txt"


def make_all():
    paths = []
    for s in STYLES:
        paths.append(sheet_for_style(s))
    paths.append(sheet_all_styles())
    sheet_failures()
    print("Contact sheets:", paths)
    return paths


if __name__ == "__main__":
    make_all()
