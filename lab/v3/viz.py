"""Panel B — semantic blueprint diagram. Readable before any material."""
from __future__ import annotations

from PIL import Image, ImageDraw, ImageFont

from lab.v3.geom2d import bbox, centroid


def _font(size):
    for name in ("DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _hex(h, alpha=255):
    h = (h or "#888888").lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    rgb = tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))
    return rgb + (alpha,)


def _fit(pts, origin, scale, flip_y, canvas_h):
    out = []
    for x, y in pts:
        sx = origin[0] + x * scale
        sy = origin[1] + (canvas_h - y * scale if False else 0)
        # normalized coords are Y-up; image is Y-down
        sy = origin[1] + (flip_y - y) * scale
        out.append((sx, sy))
    return out


def render_blueprint(bp: dict, out_png: str, size: int = 1280) -> str:
    im = Image.new("RGBA", (size, size), (247, 244, 239, 255))
    draw = ImageDraw.Draw(im)
    title_f = _font(28)
    head_f = _font(18)
    body_f = _font(15)
    small_f = _font(13)

    conf = bp.get("confidence", "?")
    conf_color = {"HIGH": (20, 120, 70), "MEDIUM": (160, 100, 20), "LOW": (150, 40, 40)}.get(conf, (40, 40, 40))
    draw.rectangle([0, 0, size, 78], fill=(255, 255, 255, 255))
    draw.text((24, 12), "SEMANTIC BLUEPRINT", font=title_f, fill=(30, 30, 30, 255))
    subtitle = f"{bp.get('subject_hypothesis')}   ·   {conf}   ·   {bp.get('orientation')}   ·   {bp.get('handler')}"
    draw.text((24, 48), subtitle, font=head_f, fill=conf_color + (255,) if len(conf_color) == 3 else conf_color)
    if conf == "LOW":
        draw.rectangle([0, 78, size, 112], fill=(255, 228, 220, 255))
        draw.text(
            (24, 86),
            "LOW CONFIDENCE — polish these strokes only. Do not invent an object.",
            font=body_f,
            fill=(120, 40, 30, 255),
        )
        top = 124
    else:
        top = 90

    # layout: drawing on the left, legend on the right
    legend_w = 430
    draw_area = (24, top + 8, size - legend_w - 16, size - 24)
    all_pts = []
    for c in bp["major_components"]:
        all_pts.extend(c.get("polygon") or c.get("path") or [])
    if not all_pts:
        all_pts = [[-0.4, -0.4], [0.4, 0.4]]
    x0, y0, x1, y1 = bbox(all_pts)
    # pad
    pad = 0.08
    x0 -= pad
    y0 -= pad
    x1 += pad
    y1 += pad
    dw = draw_area[2] - draw_area[0]
    dh = draw_area[3] - draw_area[1]
    scale = min(dw / max(x1 - x0, 1e-6), dh / max(y1 - y0, 1e-6))
    # center
    world_w = (x1 - x0) * scale
    world_h = (y1 - y0) * scale
    ox = draw_area[0] + (dw - world_w) / 2 - x0 * scale
    # y mapping: screen = oy_base - y * scale, with y1 at top
    oy_base = draw_area[1] + (dh - world_h) / 2 + y1 * scale

    def map_pts(pts):
        return [(ox + x * scale, oy_base - y * scale) for x, y in pts]

    draw.rounded_rectangle(
        [draw_area[0] - 8, draw_area[1] - 8, draw_area[2] + 8, draw_area[3] + 8],
        radius=16,
        fill=(255, 255, 255, 255),
        outline=(220, 214, 206, 255),
        width=2,
    )

    # back to front
    ordered = sorted(bp["major_components"], key=lambda c: c.get("z_order", 0))
    palette_edge = (40, 40, 48, 255)
    for c in ordered:
        col = _hex(c.get("color"), 230)
        if c.get("kind") == "open_tube":
            pts = map_pts(c.get("path") or [])
            if len(pts) >= 2:
                width = 10 if c.get("feature_scale") != "detail" else 6
                draw.line(pts, fill=col, width=width, joint="curve")
                r = 5
                draw.ellipse([pts[0][0] - r, pts[0][1] - r, pts[0][0] + r, pts[0][1] + r], fill=col)
                draw.ellipse([pts[-1][0] - r, pts[-1][1] - r, pts[-1][0] + r, pts[-1][1] + r], fill=col)
        else:
            pts = map_pts(c.get("polygon") or [])
            if len(pts) >= 3:
                draw.polygon(pts, fill=col)
                draw.line(pts + [pts[0]], fill=palette_edge, width=3)
        # label near centroid
        src = c.get("polygon") or c.get("path") or []
        if src:
            cx, cy = centroid(src)
            sx, sy = map_pts([[cx, cy]])[0]
            tag = c["id"]
            if c.get("completed"):
                tag += "*"
            draw.rounded_rectangle([sx - 4, sy - 12, sx + 8 + 7 * len(tag), sy + 10], radius=4, fill=(255, 255, 255, 230))
            draw.text((sx, sy - 10), tag, font=small_f, fill=(20, 20, 20, 255))

    # relationships as a note, not a spaghetti of arrows over the drawing
    lx = size - legend_w + 8
    y = top
    draw.text((lx, y), "COMPONENTS", font=head_f, fill=(30, 30, 30, 255))
    y += 28
    for c in bp["major_components"]:
        swatch = _hex(c.get("color"))
        draw.rectangle([lx, y + 2, lx + 14, y + 16], fill=swatch, outline=(40, 40, 40, 255))
        mark = " (completed)" if c.get("completed") else ""
        strokes = ",".join(c.get("source_strokes") or []) or "—"
        draw.text((lx + 20, y), f"{c['id']}  {c.get('name')}{mark}", font=body_f, fill=(20, 20, 20, 255))
        y += 18
        draw.text((lx + 20, y), f"strokes: {strokes}", font=small_f, fill=(90, 90, 90, 255))
        y += 20
    y += 6
    draw.text((lx, y), "RELATIONSHIPS", font=head_f, fill=(30, 30, 30, 255))
    y += 26
    for rel in bp.get("component_relationships") or []:
        if "a" in rel and "b" in rel:
            line = f"{rel['type']}: {rel['a']} → {rel['b']}"
        else:
            line = rel.get("type", "rel")
        draw.text((lx, y), line, font=small_f, fill=(40, 40, 40, 255))
        y += 16
        detail = rel.get("detail") or ""
        if detail:
            # wrap roughly
            while detail:
                draw.text((lx + 8, y), detail[:48], font=small_f, fill=(100, 100, 100, 255))
                detail = detail[48:]
                y += 15
        y += 4
        if y > size - 220:
            break

    def section(title, items, color):
        nonlocal y
        y += 8
        draw.text((lx, y), title, font=head_f, fill=color)
        y += 24
        for item in items:
            text = "• " + item
            while text:
                draw.text((lx, y), text[:46], font=small_f, fill=(40, 40, 40, 255))
                text = text[46:]
                y += 16
            if y > size - 20:
                return

    # If the component list already used the column, paint preserve lists in a
    # second pass only when there is room; otherwise they still live in JSON.
    if y < size - 200:
        section("MUST PRESERVE", bp.get("features_must_preserve") or [], (20, 90, 60, 255))
        section("MAY COMPLETE", bp.get("features_may_complete") or [], (140, 90, 20, 255))
        section("NEVER INVENT", bp.get("features_must_never_invent") or [], (140, 40, 40, 255))

    im.save(out_png)
    return out_png
