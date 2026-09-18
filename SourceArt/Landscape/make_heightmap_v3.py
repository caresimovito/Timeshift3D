"""Heightmap v3: v2 plus a carved meadow stream channel and a flooded swamp path.

Starts from Zone1_Heightmap_v2.png so every other zone stays identical.
Import exactly like v2 (same size, origin and scale).

  Meadow  (X 12600..25400): a flat-bottomed channel under the stream ribbon,
          about 45 cm deep, following the same centre line as SM_MeadowStream_v2.
  Swamp   (X 27800..36800): the dry 20 m causeway drops to -55 cm (25 cm under the
          -30 cm swamp water) with a winding string of mud islands at +10 cm.

Also writes stream_profile.json (water level per X) for rebuilding the stream mesh.
"""
import json
import math
import numpy as np
from PIL import Image

SRC = "Zone1_Heightmap_v2.png"
QUAD = 50.0
ORIGIN_X, ORIGIN_Y = -3000.0, -12600.0

hm = np.asarray(Image.open(SRC)).astype(np.float64)
h = (hm - 32768) / 1.28
NY, NX = h.shape
x = ORIGIN_X + QUAD * np.arange(NX)
y = ORIGIN_Y + QUAD * np.arange(NY)
X, Y = np.meshgrid(x, y)
h_old = h.copy()


def smoothstep(e0, e1, v):
    t = np.clip((v - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def terr(hh, px, py):
    i = (px - ORIGIN_X) / QUAD
    j = (py - ORIGIN_Y) / QUAD
    i0, j0 = int(i), int(j)
    fi, fj = i - i0, j - j0
    return (hh[j0, i0] * (1 - fi) * (1 - fj) + hh[j0, i0 + 1] * fi * (1 - fj)
            + hh[j0 + 1, i0] * (1 - fi) * fj + hh[j0 + 1, i0 + 1] * fi * fj)


# ---------------------------------------------------------------- meadow stream
def cy(xx):
    return 700 + 1000 * np.sin((xx - 13000) / 2800.0) + 250 * np.sin((xx - 13000) / 900.0)


def width(xx):
    return 550 + 110 * np.sin((xx - 13000) / 1700.0)


# distance to the centre line, measured across the local direction of the stream
dydx = (cy(X + 10) - cy(X - 10)) / 20.0
dist = np.abs(Y - cy(X)) / np.sqrt(1 + dydx ** 2)
hw = width(X) / 2
xin = smoothstep(12700, 13300, X) * (1 - smoothstep(24700, 25300, X))
channel = 45 * smoothstep(hw + 140, hw - 40, dist) * xin
bed_noise = 6 * np.sin(X / 170.0) * np.sin(Y / 230.0)
h -= channel + np.where(channel > 30, bed_noise, 0)

profile = []
for xs in range(12600, 25401, 50):
    bank = terr(h_old, xs, float(cy(xs)))
    profile.append([xs, round(bank - 14, 1)])     # water 14 cm below the old ground
json.dump({"stream_water_level": profile}, open("stream_profile.json", "w"))

# ---------------------------------------------------------------- swamp causeway
sx = smoothstep(27300, 27900, X) * (1 - smoothstep(36700, 37300, X))
corr = smoothstep(1900, 1300, np.abs(Y)) * sx         # old dry corridor plus its sloping margin
flood = -55 + 6 * np.sin(X / 260.0) * np.cos(Y / 310.0)
h = h + (np.minimum(h, flood) - h) * corr               # only ever lowers, so no levee is left behind

# mud islands: a winding chain along the walking line plus a few off to the sides
rng = np.random.default_rng(1307)
isl = np.zeros_like(h)
xs = 27900.0
while xs < 36700:
    cyv = 420 * math.sin(xs / 1300.0) + 150 * math.sin(xs / 470.0)
    for (ox, oy, s) in [(0, cyv, 1.0)] + [(rng.uniform(-300, 300), rng.choice([-1, 1]) * rng.uniform(1500, 2800), 0.8)]:
        rx, ry = rng.uniform(450, 800) * s, rng.uniform(280, 480) * s
        ang = rng.uniform(-0.5, 0.5)
        dx, dy = X - (xs + ox), Y - oy
        u = (dx * math.cos(ang) + dy * math.sin(ang)) / rx
        v = (-dx * math.sin(ang) + dy * math.cos(ang)) / ry
        r = np.sqrt(u * u + v * v)
        isl = np.maximum(isl, smoothstep(1.0, 0.55, r))
    xs += rng.uniform(1100, 1600)
island_top = 10 + 8 * np.sin(X / 90.0) * np.sin(Y / 120.0)
h = h + (np.maximum(h, island_top) - h) * isl * sx

out = np.clip(np.round(32768 + h * 1.28), 0, 65535).astype(np.uint16)
Image.fromarray(out, mode="I;16").save("Zone1_Heightmap_v3.png")

d = h - h_old
print(f"changed cells: {(np.abs(d) > 1).sum()}  min {d.min():.0f}  max {d.max():.0f} cm")
walk = sx > 0.99
print("swamp corridor heights (|Y|<900):", np.percentile(h[walk & (np.abs(Y) < 900)], [0, 25, 50, 75, 100]).round(0))
m = xin > 0.99
print("stream bed depth below old ground:", np.percentile((h_old - h)[m & (dist < hw - 60)], [5, 50, 95]).round(0))
