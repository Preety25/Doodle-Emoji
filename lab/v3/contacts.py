"""Contact sheets for V3 panels A–F."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def _font(size):
    for name in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",):
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _on_paper(im: Image.Image, paper=(244, 241, 236, 255)) -> Image.Image:
    im = im.convert("RGBA")
    bg = Image.new("RGBA", im.size, paper)
    return Image.alpha_composite(bg, im)


def _fit(im: Image.Image, cell: int) -> Image.Image:
    im = _on_paper(im)
    im.thumbnail((cell, cell), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (cell, cell), (244, 241, 236, 255))
    canvas.paste(im, ((cell - im.width) // 2, (cell - im.height) // 2), im)
    return canvas


def downsample_png(src: Path, dest: Path, size: int = 1024) -> None:
    """Premultiplied downsample so transparent edges stay clean."""
    import numpy as np

    im = Image.open(src).convert("RGBA")
    arr = np.asarray(im).astype("float32") / 255.0
    rgb = arr[..., :3] * arr[..., 3:4]
    a = arr[..., 3]
    premul = np.dstack([rgb, a])
    big = Image.fromarray((premul * 255.0).clip(0, 255).astype("uint8"), "RGBA")
    small = big.resize((size, size), Image.Resampling.LANCZOS)
    out = np.asarray(small).astype("float32") / 255.0
    alpha = out[..., 3:4]
    rgb = np.where(alpha > 1e-4, out[..., :3] / np.maximum(alpha, 1e-4), 0.0)
    merged = np.dstack([rgb, out[..., 3]])
    Image.fromarray((merged * 255.0).clip(0, 255).astype("uint8"), "RGBA").save(dest)


def example_strip(example_dir: Path, title: str, out_path: Path, cell: int = 360) -> Path:
    labels = [
        ("A_original.png", "A original"),
        ("B_blueprint.png", "B blueprint"),
        ("C_gummy.png", "C gummy"),
        ("D_clay.png", "D clay"),
        ("E_plush.png", "E plush"),
        ("F_glossy.png", "F glossy"),
    ]
    pad = 16
    header = 48
    w = pad + len(labels) * (cell + pad)
    h = header + cell + pad
    sheet = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    draw = ImageDraw.Draw(sheet)
    draw.text((pad, 12), title, font=_font(22), fill=(20, 20, 20, 255))
    for i, (name, label) in enumerate(labels):
        x = pad + i * (cell + pad)
        y = header
        path = example_dir / name
        if path.exists():
            im = _fit(Image.open(path), cell)
        else:
            im = Image.new("RGBA", (cell, cell), (230, 210, 210, 255))
        sheet.paste(im, (x, y))
        draw.text((x + 8, y + 8), label, font=_font(16), fill=(20, 20, 20, 255))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.convert("RGB").save(out_path)
    return out_path


def multi_sheet(rows: list[tuple[str, Path]], out_path: Path, cell: int = 280) -> Path:
    labels = ["A original", "B blueprint", "C gummy", "D clay", "E plush", "F glossy"]
    files = ["A_original.png", "B_blueprint.png", "C_gummy.png", "D_clay.png", "E_plush.png", "F_glossy.png"]
    pad = 12
    label_w = 150
    header = 36
    w = label_w + pad + len(files) * (cell + pad)
    h = header + len(rows) * (cell + pad) + pad
    sheet = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    draw = ImageDraw.Draw(sheet)
    font = _font(14)
    for i, lab in enumerate(labels):
        draw.text((label_w + pad + i * (cell + pad), 10), lab, font=font, fill=(30, 30, 30, 255))
    for r, (title, folder) in enumerate(rows):
        y = header + r * (cell + pad)
        draw.text((8, y + cell // 2 - 8), title, font=_font(16), fill=(20, 20, 20, 255))
        for c, name in enumerate(files):
            x = label_w + pad + c * (cell + pad)
            path = folder / name
            if path.exists():
                im = _fit(Image.open(path), cell)
            else:
                im = Image.new("RGBA", (cell, cell), (230, 210, 210, 255))
            sheet.paste(im, (x, y))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.convert("RGB").save(out_path)
    return out_path
