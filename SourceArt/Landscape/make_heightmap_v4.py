"""Heightmap v4: v3 with the meadow stream bed dug 35 cm deeper (water level unchanged).

Writes Zone1_Heightmap_v4.png (16-bit, same size/origin/scale as v3) and
Zone1_Heightmap_v4_RG.png (height packed into R=high byte, G=low byte) for the
render-target import done by Saved/import_land_v4.py.
"""
import numpy as np
from PIL import Image

QUAD = 50.0
ORIGIN_X, ORIGIN_Y = -3000.0, -12600.0
EXTRA = 35.0   # cm

hm = np.asarray(Image.open("Zone1_Heightmap_v3.png")).astype(np.float64)
h = (hm - 32768) / 1.28
NY, NX = h.shape
X, Y = np.meshgrid(ORIGIN_X + QUAD * np.arange(NX), ORIGIN_Y + QUAD * np.arange(NY))


def smoothstep(e0, e1, v):
    t = np.clip((v - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def cy(xx):
    return 700 + 1000 * np.sin((xx - 13000) / 2800.0) + 250 * np.sin((xx - 13000) / 900.0)


def width(xx):
    return 550 + 110 * np.sin((xx - 13000) / 1700.0)


dydx = (cy(X + 10) - cy(X - 10)) / 20.0
dist = np.abs(Y - cy(X)) / np.sqrt(1 + dydx ** 2)
hw = width(X) / 2
xin = smoothstep(12700, 13300, X) * (1 - smoothstep(24700, 25300, X))
# deepen only inside the existing channel so the banks (and the stones on them) stay put
deepen = EXTRA * smoothstep(hw + 20, hw - 120, dist) * xin
h -= deepen

out = np.clip(np.round(32768 + h * 1.28), 0, 65535).astype(np.uint16)
Image.fromarray(out, mode="I;16").save("Zone1_Heightmap_v4.png")
rg = np.zeros((NY, NX, 4), np.uint8)
rg[..., 0] = out >> 8
rg[..., 1] = out & 255
rg[..., 3] = 255
Image.fromarray(rg, "RGBA").save("Zone1_Heightmap_v4_RG.png")
d = (out.astype(np.int64) - hm.astype(np.int64)) / 1.28
print(f"cells changed: {(np.abs(d) > 0.5).sum()}  deepest: {d.min():.1f} cm  raised: {d.max():.1f} cm")
