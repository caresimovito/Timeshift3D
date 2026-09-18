"""Heightmap for Lvl_Era1_DinosaurEra (Zone 1, prehistoric).

Import in Landscape mode > New > Import from File with:
  Location (-3000, -9450, 0), Scale (50, 50, 100), 1 section per component, 63 quads per section.
Heightmap value 32768 = world Z 0. At Z scale 100 one unit = 100/128 cm.
"""
import numpy as np
from PIL import Image

NX, NY = 505, 379            # 8 x 6 components of 63 quads
QUAD = 50.0                  # cm per quad
ORIGIN_X, ORIGIN_Y = -3000.0, -9450.0
rng = np.random.default_rng(1908)

x = ORIGIN_X + QUAD * np.arange(NX)
y = ORIGIN_Y + QUAD * np.arange(NY)
X, Y = np.meshgrid(x, y)     # arrays are [row=Y, col=X]

# Playable corridor: the Ground_* block footprints (x0, x1, y0, y1), tops at Z = 0.
CORRIDOR = [
    (-1000, 1000, -1000, 1000),   # ArrivalPad
    (1000, 2400, -500, 500),      # PathA
    (2400, 4700, -800, 800),      # TarPitZone
    (4700, 6300, -1000, 1000),    # RaptorZone
    (6300, 7800, -900, 900),      # RockfallZone
    (7800, 8600, -1000, 1000),    # RiverBankNear
    (8800, 9800, -1000, 1000),    # RiverBankFar
    (9800, 11500, -900, 900),     # KeyArtifactPad
    (11500, 12200, -700, 700),    # ApproachToArena
    (12200, 15050, -1750, 1750),  # BossArena
]

def rect_dist(x0, x1, y0, y1):
    dx = np.maximum(np.maximum(x0 - X, X - x1), 0)
    dy = np.maximum(np.maximum(y0 - Y, Y - y1), 0)
    return np.hypot(dx, dy)

d = np.min([rect_dist(*r) for r in CORRIDOR], axis=0)   # cm from the corridor (0 inside)

def smoothstep(e0, e1, v):
    t = np.clip((v - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)

def noise(cell_cm, amp):
    """Smooth value noise: a coarse random grid upsampled bicubically."""
    gw, gh = int(NX * QUAD / cell_cm) + 3, int(NY * QUAD / cell_cm) + 3
    grid = Image.fromarray(rng.uniform(-1, 1, (gh, gw)).astype(np.float32), mode="F")
    return np.asarray(grid.resize((NX, NY), Image.BICUBIC)) * amp

fbm = noise(6000, 1.0) + noise(2500, 0.5) + noise(1000, 0.25) + noise(400, 0.12)
ridged = 1 - np.abs(noise(3000, 1.0) + noise(1200, 0.4))       # sharp crests for the volcanic side

volcanic = smoothstep(9000, 10500, X)                           # 0 = jungle, 1 = volcanic
swamp = np.exp(-(((X - 3500) / 1800) ** 2))                     # tar pit / swamp basin stays lower

# Hills beyond the corridor
hill = 450 + 900 * (fbm * 0.5 + 0.5)
hill += volcanic * (500 + 900 * np.clip(ridged, 0, 1))
hill *= 1 - 0.45 * swamp
cone = np.hypot(X - 18500, Y) / 7000                            # rise toward the background volcano
hill += 3200 * np.clip(1 - cone, 0, 1) ** 1.6
hill += np.clip((np.abs(Y) - 6500) / 2900, 0, 1) ** 1.5 * 1800  # meet the background mountains

MARGIN = 300                                                    # flat walkable strip past the block edges
h = hill * smoothstep(MARGIN, MARGIN + 2600, d)
h += noise(700, 12) * smoothstep(0, MARGIN, d)                  # slight unevenness just off the path

# Tar pit: sink 25 cm under the tar mesh (X 3350-3850, Y -250..250)
tar = smoothstep(80, 0, rect_dist(3350, 3850, -250, 250))
h -= 25 * tar

# River along X = 8700 under the bridge: 1.8 m deep channel, widening into a valley in the hills
dx = np.abs(X - 8700)
river_bed = -180 + noise(900, 25)
in_corridor = d == 0
h = np.where(in_corridor & (dx < 100), river_bed, h)
valley = smoothstep(100, 1400, dx)
h = np.where(~in_corridor, river_bed * (1 - valley) + h * valley, h)

# Encode: value 32768 = Z 0, Z scale 100 -> 1.28 units per cm
hm = np.clip(np.round(32768 + h * 1.28), 0, 65535).astype(np.uint16)
Image.fromarray(hm, mode="I;16").save("Zone1_Heightmap.png")

# Colour preview for checking (corridor outlined)
from PIL import ImageDraw
norm = (h - h.min()) / (h.max() - h.min())
rgb = (np.stack([norm * 0.9 + 0.1 * volcanic, norm * 0.8 + 0.2 * (1 - volcanic), norm * 0.6], -1) * 255).astype(np.uint8)
prev = Image.fromarray(rgb).resize((NX * 2, NY * 2), Image.NEAREST)
dr = ImageDraw.Draw(prev)
for x0, x1, y0, y1 in CORRIDOR:
    dr.rectangle([(x0 - ORIGIN_X) / QUAD * 2, (y0 - ORIGIN_Y) / QUAD * 2, (x1 - ORIGIN_X) / QUAD * 2, (y1 - ORIGIN_Y) / QUAD * 2], outline=(255, 0, 0))
prev.save("Zone1_Heightmap_preview.png")

print(f"size {NX}x{NY}, height range {h.min():.0f} .. {h.max():.0f} cm")
print(f"corridor height range {h[in_corridor & (dx >= 100)].min():.1f} .. {h[in_corridor & (dx >= 100)].max():.1f} cm")
for name, px, py in [("PlayerStart", 0, 0), ("TarPit", 3600, 0), ("Bridge", 8700, 0), ("KeyArtifact", 10600, 0), ("Portal", 14700, 0), ("Hills N of raptors", 5500, 4000), ("Volcano slope", 17500, 0)]:
    i, j = int(round((px - ORIGIN_X) / QUAD)), int(round((py - ORIGIN_Y) / QUAD))
    print(f"  {name:20} Z = {h[j, i]:7.1f} cm")
