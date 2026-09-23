"""Heightmap v6: v5 plus a natural pond basin where the Zone 2 tar pool sits (26200, 0).

The pool used to be a flat plane dropped on flat ground, so its edge cut a straight line across
the grass. This digs a real hollow for it: an irregular bowl about 18 m across with a soft rim,
an uneven floor at -140 cm, and a low lip of spoil around the outside, so the shoreline follows
the ground instead of slicing through it.

Writes Zone1_Heightmap_v6.png, Zone1_Heightmap_v6_RG.png (for Saved/import_land.py) and
pond_water_mask.npy (cells the water surface covers).
"""
import numpy as np
from PIL import Image

QUAD = 50.0
ORIGIN_X, ORIGIN_Y = -3000.0, -12600.0
CX, CY = 26200.0, 0.0
FLOOR, WATER = -140.0, -45.0

hm = np.asarray(Image.open("Zone1_Heightmap_v5.png")).astype(np.float64)
h = (hm - 32768) / 1.28
NY, NX = h.shape
X, Y = np.meshgrid(ORIGIN_X + QUAD * np.arange(NX), ORIGIN_Y + QUAD * np.arange(NY))


def smoothstep(e0, e1, v):
    t = np.clip((v - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


dx, dy = X - CX, Y - CY
dist = np.hypot(dx, dy)
th = np.arctan2(dy, dx)
# wobbly outline so no part of the shore is a straight line or a clean circle
R = 880 + 230 * np.sin(2 * th + 0.6) + 150 * np.sin(3 * th - 1.2) + 80 * np.sin(5 * th + 2.1)
rho = dist / R

floor = FLOOR + 14 * np.sin(X / 130.0) * np.cos(Y / 155.0)      # uneven bottom
bowl = smoothstep(1.02, 0.52, rho)                               # 1 in the middle, 0 past the rim
carved = h + (floor - h) * bowl
h_new = np.minimum(h, carved)                                    # only ever digs

lip = 26 * (smoothstep(0.98, 1.10, rho) * (1 - smoothstep(1.18, 1.34, rho)))
h_new = h_new + lip * (rho > 1.0)                                # low bank of spoil outside the rim

out = np.clip(np.round(32768 + h_new * 1.28), 0, 65535).astype(np.uint16)
Image.fromarray(out).save("Zone1_Heightmap_v6.png")
rg = np.zeros((NY, NX, 4), np.uint8)
rg[..., 0] = out >> 8
rg[..., 1] = out & 255
rg[..., 3] = 255
Image.fromarray(rg, "RGBA").save("Zone1_Heightmap_v6_RG.png")

hq = (out.astype(np.float64) - 32768) / 1.28
mask = (hq < WATER) & (rho < 0.97)                               # water only inside this bowl
np.save("pond_water_mask.npy", mask)

d = (out.astype(np.int64) - hm.astype(np.int64)) / 1.28
print(f"cells dug: {(d < -0.5).sum()}  deepest {d.min():.0f} cm  raised {d.max():.1f} cm")
print(f"water cells: {mask.sum()}  pond width x: {(mask.any(axis=0)).sum() * QUAD / 100:.0f} m"
      f"  y: {(mask.any(axis=1)).sum() * QUAD / 100:.0f} m")
print("changes outside the pond:", ((np.abs(d) > 0.5) & (dist > 2200)).sum())
