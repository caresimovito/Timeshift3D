"""Heightmap for the extended Lvl_Era1_DinosaurEra (~1 km, 17 zones).

Import in Landscape mode > New > Import from File with:
  Location (52125, 0, 0)  <- the dialog's Location is the landscape CENTER
  Scale (50, 50, 100), 1 section per component, 63 quads per section.
  Resulting landscape covers X -3000..107250, Y -12600..12600.
Heightmap value 32768 = world Z 0. At Z scale 100 one unit = 100/128 cm.

Also writes zone_layout.json: zone X ranges plus the old->new X mapping used to
move existing gameplay actors from the original 150 m layout.
"""
import json
import numpy as np
from PIL import Image, ImageDraw

NX, NY = 63 * 35 + 1, 63 * 8 + 1      # 2206 x 505 vertices
QUAD = 50.0
ORIGIN_X, ORIGIN_Y = -3000.0, -12600.0
rng = np.random.default_rng(1908)

x = ORIGIN_X + QUAD * np.arange(NX)
y = ORIGIN_Y + QUAD * np.arange(NY)
X, Y = np.meshgrid(x, y)

# (name, x0, x1, half_width, new_zone)
ZONES = [
    ("ArrivalPad",       -1000,  1000, 1000, False),
    ("PathA",             1000, 13000,  500, False),
    ("GrazingMeadow",    13000, 25000, 1500, True),
    ("TarPit",           25000, 27300,  800, False),
    ("SwampMarsh",       27300, 37300, 1000, True),
    ("RaptorZone",       37300, 38900, 1000, False),
    ("NestingGrounds",   38900, 48900, 1500, True),
    ("RockfallZone",     48900, 51900,  900, False),
    ("CanyonPass",       51900, 63900,  400, True),
    ("RiverBankNear",    63900, 64700, 1000, False),
    ("RiverBankFar",     64900, 65900, 1000, False),
    ("AshForest",        65900, 77900, 1000, True),
    ("KeyArtifactPad",   77900, 79600,  900, False),
    ("LavaFields",       79600, 91600,  700, True),
    ("ApproachToArena",  91600, 94600,  700, False),
    ("BossArena",        94600, 97450, 1750, False),
]
RIVER_X = 64800

# Old (150 m) layout -> new layout, piecewise linear on [old0, old1)
X_MAP = [
    (-1e9,   1000,  None, None),          # identity
    (1000,   2400,  1000, 13000),
    (2400,   4700, 25000, 27300),
    (4700,   6300, 37300, 38900),
    (6300,   7800, 48900, 51900),
    (7800,   8600, 63900, 64700),
    (8600,   8800, 64700, 64900),
    (8800,   9800, 64900, 65900),
    (9800,  11500, 77900, 79600),
    (11500, 12200, 91600, 94600),
    (12200, 15050, 94600, 97450),
    (15050,  1e9,  None, None),           # shift by +82400
]


def rect_dist(x0, x1, y0, y1):
    dx = np.maximum(np.maximum(x0 - X, X - x1), 0)
    dy = np.maximum(np.maximum(y0 - Y, Y - y1), 0)
    return np.hypot(dx, dy)


def smoothstep(e0, e1, v):
    t = np.clip((v - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def band(x0, x1, fade):
    """1 inside [x0, x1] along X, fading to 0 over `fade` cm."""
    return smoothstep(x0 - fade, x0, X) * (1 - smoothstep(x1, x1 + fade, X))


def noise(cell_cm, amp):
    gw, gh = int(NX * QUAD / cell_cm) + 3, int(NY * QUAD / cell_cm) + 3
    grid = Image.fromarray(rng.uniform(-1, 1, (gh, gw)).astype(np.float32), mode="F")
    return np.asarray(grid.resize((NX, NY), Image.BICUBIC)) * amp


d = np.min([rect_dist(x0, x1, -hw, hw) for _, x0, x1, hw, _ in ZONES], axis=0)
fbm = noise(6000, 1.0) + noise(2500, 0.5) + noise(1000, 0.25) + noise(400, 0.12)
ridged = np.clip(1 - np.abs(noise(3000, 1.0) + noise(1200, 0.4)), 0, 1)

volcanic = smoothstep(65500, 67000, X)
meadow = band(13000, 25000, 2500)
swamp = band(25000, 37300, 2000)
nesting = band(38900, 48900, 1500)
canyon = band(51900, 63900, 800)
lava = band(79600, 91600, 1500)

hill = 450 + 900 * (fbm * 0.5 + 0.5)
hill *= 1 - 0.55 * meadow                                          # wide, gentle valley
hill *= 1 - 0.5 * swamp                                            # low basin
hill += nesting * (300 + 1100 * ridged)                            # rocky outcrops round the nests
hill += volcanic * (1 - lava) * (500 + 900 * ridged)               # ridges in the ash forest / approach
hill = hill * (1 - canyon) + canyon * (2600 + 900 * (fbm * 0.5 + 0.5))   # tall gorge walls
hill += np.clip((np.abs(Y) - 8000) / 4600, 0, 1) ** 1.5 * 2200     # meet the background mountains
cone = np.hypot(X - 104000, Y) / 9000
hill += 4500 * np.clip(1 - cone, 0, 1) ** 1.6                      # rise toward the volcano

MARGIN = 300
rise = 2600 * (1 - canyon) + 500 * canyon                          # canyon walls rise fast
h = hill * smoothstep(MARGIN, MARGIN + rise, d)
h += noise(700, 12) * smoothstep(0, MARGIN, d)

# Swamp marsh: flooded flats either side of the path (water plane goes at about -40)
flats = swamp * smoothstep(MARGIN, MARGIN + 400, d) * (1 - smoothstep(2500, 5000, d))
h = h * (1 - flats) + (-90 + noise(600, 15)) * flats

# Lava fields: sunken plain around the rock path for lava flows, low outcrops further out
lava_flat = lava * smoothstep(MARGIN, MARGIN + 300, d) * (1 - smoothstep(3500, 6500, d))
h = h * (1 - lava_flat) + (-120 + 80 * ridged) * lava_flat

# Tar pit (old X 3350-3850 -> 25950-26450)
h -= 25 * smoothstep(80, 0, rect_dist(25950, 26450, -250, 250))

# River channel
dxr = np.abs(X - RIVER_X)
river_bed = -180 + noise(900, 25)
in_corridor = d == 0
h = np.where(in_corridor & (dxr < 100), river_bed, h)
valley = smoothstep(100, 1400, dxr)
h = np.where(~in_corridor, river_bed * (1 - valley) + h * valley, h)

hm = np.clip(np.round(32768 + h * 1.28), 0, 65535).astype(np.uint16)
Image.fromarray(hm, mode="I;16").save("Zone1_Heightmap_v2.png")

norm = (h - h.min()) / (h.max() - h.min())
rgb = (np.stack([norm * 0.9 + 0.1 * volcanic, norm * 0.8 + 0.2 * (1 - volcanic), norm * 0.6], -1) * 255).astype(np.uint8)
prev = Image.fromarray(rgb)
dr = ImageDraw.Draw(prev)
for name, x0, x1, hw, new in ZONES:
    dr.rectangle([(x0 - ORIGIN_X) / QUAD, (-hw - ORIGIN_Y) / QUAD, (x1 - ORIGIN_X) / QUAD, (hw - ORIGIN_Y) / QUAD],
                 outline=(0, 255, 255) if new else (255, 0, 0))
prev.save("Zone1_Heightmap_v2_preview.png")

json.dump({"zones": [{"name": n, "x0": a, "x1": b, "half_width": w, "new": nw} for n, a, b, w, nw in ZONES],
           "river_x": RIVER_X, "x_map_old_to_new": X_MAP,
           "landscape": {"origin": [ORIGIN_X, ORIGIN_Y], "size_verts": [NX, NY], "quad_cm": QUAD,
                         "import_center": [ORIGIN_X + (NX - 1) * QUAD / 2, ORIGIN_Y + (NY - 1) * QUAD / 2, 0]}},
          open("zone_layout.json", "w"), indent=1)

print(f"size {NX}x{NY}, height range {h.min():.0f} .. {h.max():.0f} cm")
walk = in_corridor & (dxr >= 100)
print(f"corridor height range {h[walk].min():.1f} .. {h[walk].max():.1f} cm")
