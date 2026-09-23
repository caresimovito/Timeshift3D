"""Heightmap v7: break up the dead-flat ground so the walking corridor stops reading as a path.

v3-v6 kept the causeway (|Y| < 1000) at exactly height 0, and much of the surrounding plain is
flat too, so from the ground it looks like a graded road. This rolls gentle multi-octave
undulation into every cell that is currently flat: long swells, smaller hummocks, and a little
surface roughness. Nothing steep enough to catch the player, and the shaped features - pond
basins, lava channels, cliffs, river beds - are left exactly as they were.

Writes Zone1_Heightmap_v7.png and Zone1_Heightmap_v7_RG.png (for Saved/import_land.py), plus
Zone1_v7_delta.npy so placed props can be nudged by the same amount they moved.
"""
import numpy as np
from PIL import Image

QUAD = 50.0
ORIGIN_X, ORIGIN_Y = -3000.0, -12600.0
PONDS = [(26200.0, 0.0, 1500.0),      # the moss pond basin
         (29700.0, 0.0, 2600.0)]      # the zone 2 swamp

hm = np.asarray(Image.open("Zone1_Heightmap_v6.png")).astype(np.float64)
h = (hm - 32768) / 1.28
NY, NX = h.shape
X, Y = np.meshgrid(ORIGIN_X + QUAD * np.arange(NX), ORIGIN_Y + QUAD * np.arange(NY))


def smoothstep(e0, e1, v):
    t = np.clip((v - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


# --- where is the ground currently flat? (max-min over a 5x5 window is tiny)
def local_range(a, r=2):
    lo = a.copy()
    hi = a.copy()
    for d in range(1, r + 1):
        for sh in (d, -d):
            lo = np.minimum(lo, np.roll(a, sh, axis=0))
            lo = np.minimum(lo, np.roll(a, sh, axis=1))
            hi = np.maximum(hi, np.roll(a, sh, axis=0))
            hi = np.maximum(hi, np.roll(a, sh, axis=1))
    return hi - lo


rng = local_range(h)
flat = rng < 9.0
for cx, cy, rad in PONDS:                      # leave the water basins and their shores alone
    flat &= np.hypot(X - cx, Y - cy) > rad
# fade the noise out over 3 m so it never meets a shaped feature with a step
weight = smoothstep(0.0, 1.0, flat.astype(np.float64))
for _ in range(6):
    weight = 0.25 * (np.roll(weight, 1, axis=0) + np.roll(weight, -1, axis=0) +
                     np.roll(weight, 1, axis=1) + np.roll(weight, -1, axis=1))
weight = np.clip(weight, 0.0, 1.0)   # smoothed, not re-masked: no step at the boundary


def wave(ax, ay, amp, phase):
    return amp * np.sin(X / ax + phase) * np.sin(Y / ay + phase * 1.7)


# long swells, then hummocks, then surface roughness
noise = (wave(2300.0, 1900.0, 11.0, 0.0)
         + wave(1300.0, 1050.0, 7.0, 1.3)
         + wave(640.0, 520.0, 4.5, 2.7)
         + wave(310.0, 260.0, 2.5, 0.8)
         + wave(150.0, 130.0, 1.5, 2.1))
# a second, out-of-phase set so the pattern does not repeat visibly along the corridor
noise += (wave(1750.0, 2600.0, 8.0, 4.2)
          + wave(830.0, 1450.0, 5.0, 5.1)
          + wave(410.0, 350.0, 3.0, 3.3))

h_new = h + noise * weight

out = np.clip(np.round(32768 + h_new * 1.28), 0, 65535).astype(np.uint16)
Image.fromarray(out).save("Zone1_Heightmap_v7.png")
rg = np.zeros((NY, NX, 4), np.uint8)
rg[..., 0] = out >> 8
rg[..., 1] = out & 255
rg[..., 3] = 255
Image.fromarray(rg, "RGBA").save("Zone1_Heightmap_v7_RG.png")

delta = (out.astype(np.float64) - 32768) / 1.28 - h
np.save("Zone1_v7_delta.npy", delta)

corridor = np.abs(Y) < 1000
print(f"flat cells rolled: {flat.sum()} of {flat.size} ({100.0 * flat.mean():.0f}%)")
print(f"height change: min {delta.min():.1f} cm  max {delta.max():.1f} cm  mean abs {np.abs(delta).mean():.1f} cm")
gx = np.abs(np.diff(noise * weight, axis=1)) / QUAD
gy = np.abs(np.diff(noise * weight, axis=0)) / QUAD
print(f"slope added by the undulation: max {100 * max(gx.max(), gy.max()):.1f}% "
      f"(a walkable slope is under 45%)")
print(f"corridor still flat cells: {(np.abs(delta[corridor]) < 0.5).sum()} of {corridor.sum()}")
