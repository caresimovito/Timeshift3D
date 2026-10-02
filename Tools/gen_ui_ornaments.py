"""Generate the Chronoshift Temporal Log instrument ornaments.

Gears, clock faces and gauge dials for the margins of the Temporal Log. These
are regular geometry - involute-ish cog teeth, evenly spaced ticks, radial hands
- so they are generated rather than painted.

    python Tools/gen_ui_ornaments.py

Everything is drawn at SS x resolution and downsampled, which is what gives the
circles and tooth flanks clean edges. Backgrounds are transparent so the pieces
sit over the frame art. Writes PNGs to SourceArt/UI/.
"""

import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "SourceArt", "UI")
SS = 4  # supersample factor

B_EDGE = (44, 32, 14)
B_DARK = (86, 64, 29)
B_MID = (146, 114, 56)
B_LIT = (206, 172, 104)
B_HI = (242, 220, 164)

DIAL_FACE = (12, 22, 29)
DIAL_FACE_LIT = (26, 44, 54)
CYAN_DIM = (26, 92, 108)
CYAN = (86, 206, 226)
CYAN_HI = (190, 244, 252)

FONT = "C:/Windows/Fonts/georgia.ttf"


def polar(cx, cy, r, a):
    return (cx + r * math.cos(a), cy + r * math.sin(a))


def ring(draw, cx, cy, r0, r1, profile):
    """Concentric circles from r1 inward to r0, ramping through profile."""
    n = len(profile)
    span = r1 - r0
    for i in range(n):
        t = i / max(1, n - 1)
        r = r1 - span * t
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=profile[i],
                     width=max(1, int(span / n) + 1))


def shade(img, strength=0.30, angle=-0.7):
    """Directional light across the piece, applied only where it is opaque."""
    a = np.asarray(img).astype(np.float32)
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    nx, ny = math.cos(angle), math.sin(angle)
    g = ((xx / w) * nx + (yy / h) * ny)
    g = (g - g.min()) / max(1e-6, (g.max() - g.min()))
    mul = (1.0 + strength) - 2.0 * strength * g
    a[:, :, :3] = np.clip(a[:, :, :3] * mul[:, :, None], 0, 255)
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def gear(size, teeth, *, tip=0.50, root=0.40, rim=0.30, bore=0.11, spokes=6,
         spoke_w=0.085, body=B_MID):
    """Cog with trapezoidal teeth, a spoked web and a central bore."""
    s = size * SS
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = s / 2.0
    R, r = s * tip, s * root

    pts = []
    step = 2 * math.pi / teeth
    for i in range(teeth):
        a0 = i * step
        # root -> flank -> tip land -> flank -> root
        pts += [polar(c, c, r, a0 + step * 0.06),
                polar(c, c, R, a0 + step * 0.26),
                polar(c, c, R, a0 + step * 0.50),
                polar(c, c, r, a0 + step * 0.70)]
    d.polygon(pts, fill=body + (255,), outline=B_EDGE + (255,))

    # rim bevel
    rr = s * rim
    ring(d, c, c, rr * 0.88, r * 0.99, [B_LIT, B_HI, B_LIT, B_MID, B_DARK])
    d.ellipse([c - rr, c - rr, c + rr, c + rr], fill=body + (255,),
              outline=B_DARK + (255,), width=max(1, SS))

    # spoke web: punch transparent slots between hub and rim
    hub = s * (bore + 0.07)
    for i in range(spokes):
        a = (i + 0.5) * 2 * math.pi / spokes
        slot = []
        half = spoke_w * math.pi
        for t in np.linspace(a - math.pi / spokes + half, a + math.pi / spokes - half, 24):
            slot.append(polar(c, c, rr * 0.86, t))
        for t in np.linspace(a + math.pi / spokes - half, a - math.pi / spokes + half, 24):
            slot.append(polar(c, c, hub * 1.08, t))
        d.polygon(slot, fill=(0, 0, 0, 0))

    # hub + bore
    d.ellipse([c - hub, c - hub, c + hub, c + hub], fill=B_LIT + (255,),
              outline=B_EDGE + (255,), width=max(1, SS))
    b = s * bore
    d.ellipse([c - b, c - b, c + b, c + b], fill=(0, 0, 0, 0))
    d.ellipse([c - b, c - b, c + b, c + b], outline=B_EDGE + (255,), width=max(1, SS))

    return shade(img.resize((size, size), Image.LANCZOS))


def clock(size, hour=2, minute=40):
    """Brass-bezel clock: dark dial, minute ticks, numerals, two hands."""
    s = size * SS
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = s / 2.0
    out_r = s * 0.49

    # bezel
    d.ellipse([c - out_r, c - out_r, c + out_r, c + out_r],
              fill=B_MID + (255,), outline=B_EDGE + (255,), width=max(1, SS))
    ring(d, c, c, out_r * 0.80, out_r * 0.985, [B_HI, B_LIT, B_MID, B_DARK, B_EDGE])

    # dial
    face = out_r * 0.80
    d.ellipse([c - face, c - face, c + face, c + face],
              fill=DIAL_FACE + (255,), outline=B_DARK + (255,), width=max(1, SS))
    for i in range(10):
        t = i / 9.0
        rr = face * (1.0 - 0.14 * t)
        col = tuple(int(DIAL_FACE_LIT[k] + (DIAL_FACE[k] - DIAL_FACE_LIT[k]) * t)
                    for k in range(3))
        d.ellipse([c - rr, c - rr, c + rr, c + rr], outline=col, width=max(1, SS))

    # ticks
    for i in range(60):
        a = -math.pi / 2 + i * math.pi / 30
        major = (i % 5 == 0)
        r0 = face * (0.80 if major else 0.89)
        w = max(1, int(SS * (2.2 if major else 1.0)))
        d.line([polar(c, c, r0, a), polar(c, c, face * 0.95, a)],
               fill=(B_HI if major else B_MID) + (255,), width=w)

    # numerals at the quarters
    try:
        f = ImageFont.truetype(FONT, int(face * 0.26))
        for num, a in ((12, -math.pi / 2), (3, 0), (6, math.pi / 2), (9, math.pi)):
            x, y = polar(c, c, face * 0.64, a)
            d.text((x, y), str(num), font=f, fill=B_HI + (255,), anchor="mm")
    except OSError:
        pass

    # hands
    ha = -math.pi / 2 + (hour % 12 + minute / 60.0) * math.pi / 6
    ma = -math.pi / 2 + minute * math.pi / 30
    d.line([(c, c), polar(c, c, face * 0.50, ha)], fill=B_HI + (255,),
           width=max(2, int(SS * 2.6)))
    d.line([(c, c), polar(c, c, face * 0.74, ma)], fill=B_LIT + (255,),
           width=max(1, int(SS * 1.7)))
    pin = s * 0.022
    d.ellipse([c - pin, c - pin, c + pin, c + pin], fill=B_EDGE + (255,))

    return shade(img.resize((size, size), Image.LANCZOS), strength=0.22)


def dial(size, sweep=0.62):
    """Cyan temporal gauge: glowing arc, tick ladder and a pointer."""
    s = size * SS
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = s / 2.0
    out_r = s * 0.49

    d.ellipse([c - out_r, c - out_r, c + out_r, c + out_r],
              fill=B_DARK + (255,), outline=B_EDGE + (255,), width=max(1, SS))
    ring(d, c, c, out_r * 0.84, out_r * 0.985, [B_LIT, B_MID, B_DARK, B_EDGE])

    face = out_r * 0.84
    d.ellipse([c - face, c - face, c + face, c + face], fill=(6, 18, 24, 255))
    # inner glow
    for i in range(14):
        t = i / 13.0
        rr = face * (1.0 - 0.30 * t)
        col = tuple(int(CYAN_DIM[k] + ((6, 18, 24)[k] - CYAN_DIM[k]) * t) for k in range(3))
        d.ellipse([c - rr, c - rr, c + rr, c + rr], outline=col, width=max(1, SS))

    # arc ladder over the live sweep
    a0, a1 = math.radians(140), math.radians(400)
    for i in range(25):
        t = i / 24.0
        a = a0 + (a1 - a0) * t
        lit = t <= sweep
        r0 = face * (0.62 if i % 4 == 0 else 0.72)
        d.line([polar(c, c, r0, a), polar(c, c, face * 0.86, a)],
               fill=((CYAN_HI if i % 4 == 0 else CYAN) if lit else CYAN_DIM) + (255,),
               width=max(1, int(SS * (2.0 if i % 4 == 0 else 1.1))))

    # pointer
    pa = a0 + (a1 - a0) * sweep
    tipp = polar(c, c, face * 0.58, pa)
    l = polar(c, c, face * 0.12, pa + 2.4)
    r = polar(c, c, face * 0.12, pa - 2.4)
    d.polygon([tipp, l, r], fill=CYAN_HI + (255,))
    pin = s * 0.035
    d.ellipse([c - pin, c - pin, c + pin, c + pin], fill=B_LIT + (255,),
              outline=B_EDGE + (255,), width=max(1, SS))

    return shade(img.resize((size, size), Image.LANCZOS), strength=0.18)


def medallion(size):
    """Plain brass disc. A TextBlock sits on top, so no numeral is baked in."""
    s = size * SS
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = s / 2.0
    out_r = s * 0.48
    d.ellipse([c - out_r, c - out_r, c + out_r, c + out_r],
              fill=B_MID + (255,), outline=B_EDGE + (255,), width=max(1, SS))
    ring(d, c, c, out_r * 0.74, out_r * 0.98, [B_HI, B_LIT, B_MID, B_DARK])
    face = out_r * 0.74
    d.ellipse([c - face, c - face, c + face, c + face],
              fill=DIAL_FACE + (255,), outline=B_DARK + (255,), width=max(1, SS))
    # knurling around the rim
    for i in range(36):
        a = i * math.pi / 18
        d.line([polar(c, c, out_r * 0.84, a), polar(c, c, out_r * 0.96, a)],
               fill=B_DARK + (255,), width=max(1, SS))
    return shade(img.resize((size, size), Image.LANCZOS), strength=0.26)


SPECS = [
    ("T_UI_GearLarge", lambda: gear(256, 18, spokes=6)),
    ("T_UI_GearMid", lambda: gear(192, 14, spokes=5, bore=0.12)),
    ("T_UI_GearSmall", lambda: gear(128, 11, spokes=4, bore=0.14, body=B_DARK)),
    ("T_UI_ClockFace", lambda: clock(256, hour=2, minute=40)),
    ("T_UI_ClockSmall", lambda: clock(160, hour=10, minute=10)),
    ("T_UI_DialTemporal", lambda: dial(224, sweep=0.62)),
    ("T_UI_Medallion", lambda: medallion(128)),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, build in SPECS:
        img = build()
        path = os.path.normpath(os.path.join(OUT, name + ".png"))
        img.save(path)
        print("%-20s %4dpx  %s" % (name, img.width, path))


if __name__ == "__main__":
    main()
