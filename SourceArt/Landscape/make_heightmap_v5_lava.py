"""Heightmap v5: v3 plus two winding lava-river channels in the Lava Fields basins (Zone 4).

The path causeway (|Y| < 1000, height 0) is untouched. Each river sits in one of the low basins
beside it (Y roughly +-1600..+-4400), is 3.5-5.5 m wide with a bed at -175 cm, and tapers to a
point at both ends so the lava (surface at -135 cm) starts and stops naturally.

Writes Zone1_Heightmap_v5.png, Zone1_Heightmap_v5_RG.png (for Saved/import_land.py) and
lava_river_mask.npy (cells that hold lava, dilated, for the lava surface mesh).
"""
import numpy as np
from PIL import Image
from collections import deque

QUAD = 50.0
ORIGIN_X, ORIGIN_Y = -3000.0, -12600.0
BED, LAVA = -175.0, -135.0

hm = np.asarray(Image.open("Zone1_Heightmap_v3.png")).astype(np.float64)
h = (hm - 32768) / 1.28
NY, NX = h.shape
X, Y = np.meshgrid(ORIGIN_X + QUAD * np.arange(NX), ORIGIN_Y + QUAD * np.arange(NY))


def smoothstep(e0, e1, v):
    t = np.clip((v - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


RIVERS = [
    # (centre line y(x), x start, x end)
    (lambda x: -2800 + 900 * np.sin((x - 79500) / 1900.0) + 300 * np.sin((x - 79500) / 700.0), 80300, 91200),
    (lambda x: 2900 + 900 * np.sin((x - 80000) / 2100.0 + 1.3) + 300 * np.sin(x / 650.0), 79900, 90900),
]

h_new = h.copy()
for cy, x0, x1 in RIVERS:
    dydx = (cy(X + 10) - cy(X - 10)) / 20.0
    dist = np.abs(Y - cy(X)) / np.sqrt(1 + dydx ** 2)
    taper = smoothstep(x0, x0 + 900, X) * (1 - smoothstep(x1 - 900, x1, X))
    half = (210 + 70 * np.sin(X / 1500.0)) * taper + 1e-3          # half width shrinks to 0 at the ends
    d = smoothstep(half + 260, half - 40, dist) * np.clip(taper * 1.4, 0, 1)
    carved = h + (BED + 6 * np.sin(X / 230.0) - h) * d
    h_new = np.minimum(h_new, carved)                                 # only ever digs

out = np.clip(np.round(32768 + h_new * 1.28), 0, 65535).astype(np.uint16)
Image.fromarray(out).save("Zone1_Heightmap_v5.png")
rg = np.zeros((NY, NX, 4), np.uint8)
rg[..., 0] = out >> 8; rg[..., 1] = out & 255; rg[..., 3] = 255
Image.fromarray(rg, "RGBA").save("Zone1_Heightmap_v5_RG.png")

# lava cells: below the lava level, inside the Lava Fields basins, connected to a river channel
hq = (out.astype(np.float64) - 32768) / 1.28
basin = (X > 79000) & (X < 92000) & (np.abs(Y) > 1100) & (np.abs(Y) < 4800)
below = (hq < LAVA) & basin
chan = below & (hq < BED + 25)
seen = np.zeros_like(below); q = deque(zip(*np.nonzero(chan)))
for j, i in q: seen[j, i] = True
while q:
    j, i = q.popleft()
    for dj, di in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        a, b = j + dj, i + di
        if 0 <= a < NY and 0 <= b < NX and below[a, b] and not seen[a, b]:
            seen[a, b] = True; q.append((a, b))
m = seen.copy()
for _ in range(2):
    m2 = m.copy(); m2[1:] |= m[:-1]; m2[:-1] |= m[1:]; m2[:, 1:] |= m[:, :-1]; m2[:, :-1] |= m[:, 1:]; m = m2
np.save("lava_river_mask.npy", m)
d = (out.astype(np.int64) - hm.astype(np.int64)) / 1.28
print(f"cells dug: {(d < -0.5).sum()}  deepest {d.min():.0f} cm  raised {d.max():.1f} cm  lava cells {seen.sum()}")
print("path corridor touched:", ((np.abs(d) > 0.5) & (np.abs(Y) < 1100)).sum())
