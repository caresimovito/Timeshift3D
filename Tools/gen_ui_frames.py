"""Generate the Chronoshift Temporal Log 9-slice UI frame textures.

Each texture is authored at the pixel size it should render at: the border band
is a fixed number of pixels and the slice margin is set just outside it, so
Slate stretches only the flat centre and the frame stays crisp at any panel
size. Corner ornaments live entirely inside the margin square.

    python Tools/gen_ui_frames.py

Writes PNGs to SourceArt/UI/. Import with Tools/import_ui_frames.py in-editor.
The margin each texture needs is printed as a 0..1 fraction, which is what
goes into the SlateBrush Margin field.
"""

import os

import numpy as np
from PIL import Image, ImageDraw

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "SourceArt", "UI")

# brass ramp, dark -> highlight
B_EDGE = (46, 34, 15)
B_DARK = (88, 66, 30)
B_MID = (146, 114, 56)
B_LIT = (206, 172, 104)
B_HI = (238, 214, 158)

TEAL_PANEL = (14, 27, 31)
TEAL_DEEP = (9, 28, 35)
NAVY = (9, 16, 22)
PARCHMENT = (228, 216, 188)
PARCHMENT_EDGE = (190, 172, 134)
ROW_IDLE = (17, 33, 37)
ROW_SEL = (34, 58, 57)
META = (6, 19, 25)

# Concentric colour profiles, outermost first. len(profile) == band width in px.
HEAVY = [B_EDGE, B_DARK, B_MID, B_LIT, B_HI, B_LIT, B_MID, B_DARK,
         B_EDGE, B_MID, B_LIT, B_MID, B_DARK, B_EDGE]
LIGHT = [B_EDGE, B_DARK, B_MID, B_LIT, B_MID, B_DARK, B_EDGE]
THIN = [B_EDGE, B_MID, B_LIT, B_MID, B_EDGE]


def band(draw, size, profile):
    """Draw a concentric bevelled band inset from the texture edge."""
    for i, col in enumerate(profile):
        draw.rectangle([i, i, size - 1 - i, size - 1 - i], outline=col)


def rosette(draw, cx, cy, r):
    """Diamond corner ornament. Must fit inside the slice margin."""
    draw.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], fill=B_EDGE)
    r2 = max(1, int(r * 0.66))
    draw.polygon([(cx, cy - r2), (cx + r2, cy), (cx, cy + r2), (cx - r2, cy)], fill=B_LIT)
    r3 = max(1, int(r * 0.30))
    draw.polygon([(cx, cy - r3), (cx + r3, cy), (cx, cy + r3), (cx - r3, cy)], fill=B_EDGE)


def bracket(draw, size, margin, b, arm, thick):
    """Four L brackets tucked just inside the band."""
    o = b + 1
    hi = size - 1 - o
    for x, sx in ((o, 1), (hi, -1)):
        for y, sy in ((o, 1), (hi, -1)):
            draw.rectangle(sorted_box(x, y, x + sx * arm, y + sy * thick), fill=B_LIT)
            draw.rectangle(sorted_box(x, y, x + sx * thick, y + sy * arm), fill=B_LIT)


def sorted_box(x0, y0, x1, y1):
    return [min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)]


def shade(img, strength=0.16):
    """Vertical light falloff so panels read as lit from above."""
    a = np.asarray(img).astype(np.float32)
    h = a.shape[0]
    ramp = np.linspace(1.0 + strength, 1.0 - strength, h, dtype=np.float32)[:, None]
    a[:, :, :3] = np.clip(a[:, :, :3] * ramp[:, :, None], 0, 255)
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def grain(img, amount=3.0, seed=7):
    """Very light value noise so large flats do not band. Luma only."""
    rng = np.random.default_rng(seed)
    a = np.asarray(img).astype(np.float32)
    n = rng.normal(0.0, amount, size=a.shape[:2]).astype(np.float32)
    # 3x3 box blur so the grain clumps slightly instead of reading as dither
    p = np.pad(n, 1, mode="edge")
    n = sum(p[dy:dy + n.shape[0], dx:dx + n.shape[1]]
            for dy in range(3) for dx in range(3)) / 9.0
    a[:, :, :3] = np.clip(a[:, :, :3] + n[:, :, None], 0, 255)
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def panel(size, margin, profile, fill, *, orn=None, glow=None, keyline=None,
          open_bottom=False, seed=7):
    img = Image.new("RGBA", (size, size), fill + (255,))
    d = ImageDraw.Draw(img)
    b = len(profile)
    band(d, size, profile)

    if glow:
        for i in range(5):
            t = i / 4.0
            c = tuple(int(round(glow[k] + (fill[k] - glow[k]) * t)) for k in range(3))
            d.rectangle([b + i, b + i, size - 1 - b - i, size - 1 - b - i], outline=c)

    if keyline:
        d.rectangle([b + 2, b + 2, size - 3 - b, size - 3 - b], outline=keyline)

    if orn == "rosette":
        r = max(3, (margin - b) // 2)
        c0 = b + r + 1
        for cx, cy in ((c0, c0), (size - 1 - c0, c0),
                       (c0, size - 1 - c0), (size - 1 - c0, size - 1 - c0)):
            rosette(d, cx, cy, r)
    elif orn == "bracket":
        bracket(d, size, margin, b, margin - b - 2, max(2, b // 3))

    img = grain(shade(img), seed=seed)
    if open_bottom:
        # tabs read as attached to the panel below
        d2 = ImageDraw.Draw(img)
        d2.rectangle([b, size - b, size - 1 - b, size - 1], fill=fill + (255,))
    return img


def rail(size, margin):
    """Vertical timeline track: recessed channel between brass rails."""
    img = Image.new("RGBA", (size, size), TEAL_DEEP + (255,))
    d = ImageDraw.Draw(img)
    band(d, size, THIN)
    mid, w = size // 2, max(2, size // 8)
    d.rectangle([mid - w, len(THIN), mid + w, size - 1 - len(THIN)], fill=(4, 13, 18))
    d.line([(mid - w, len(THIN)), (mid - w, size - 1 - len(THIN))], fill=B_EDGE)
    d.line([(mid + w, len(THIN)), (mid + w, size - 1 - len(THIN))], fill=B_MID)
    return grain(img, amount=2.0, seed=11)


SPECS = [
    # name, size, margin, builder
    ("T_UI_FrameOuter", 72, 28,
     lambda: panel(72, 28, HEAVY, NAVY, orn="bracket", seed=2)),
    ("T_UI_PanelDark", 40, 16,
     lambda: panel(40, 16, LIGHT, TEAL_PANEL, orn="rosette", seed=4)),
    ("T_UI_PanelAnalyzer", 40, 16,
     lambda: panel(40, 16, LIGHT, TEAL_DEEP, glow=(38, 104, 118), seed=6)),
    ("T_UI_PanelParchment", 40, 16,
     lambda: panel(40, 16, LIGHT, PARCHMENT, orn="rosette", keyline=PARCHMENT_EDGE, seed=8)),
    ("T_UI_MetaBar", 24, 10, lambda: panel(24, 10, THIN, META, seed=9)),
    ("T_UI_RowIdle", 24, 10, lambda: panel(24, 10, THIN, ROW_IDLE, seed=12)),
    ("T_UI_RowSelected", 24, 10,
     lambda: panel(24, 10, LIGHT, ROW_SEL, keyline=B_LIT, seed=13)),
    ("T_UI_TabActive", 40, 16,
     lambda: panel(40, 16, LIGHT, (72, 55, 24), open_bottom=True, seed=3)),
    ("T_UI_TabIdle", 40, 16,
     lambda: panel(40, 16, THIN, TEAL_PANEL, open_bottom=True, seed=5)),
    ("T_UI_Rail", 32, 12, lambda: rail(32, 12)),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    print("%-22s %5s  %-8s %s" % ("texture", "px", "margin", "file"))
    for name, size, margin, build in SPECS:
        path = os.path.normpath(os.path.join(OUT, name + ".png"))
        build().save(path)
        print("%-22s %5d  %.4f   %s" % (name, size, margin / size, path))


if __name__ == "__main__":
    main()
