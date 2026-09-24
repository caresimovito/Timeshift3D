"""Heightmap v10 (was v9, narrowed): give the jungle corridor a floor that isn't a table top.

v7 already rolled this ground, but almost all of its amplitude sat in 20-25 m swells, which
tilt the ground without ever making it *uneven* - the meadow still measures 78% flat at a
2.5 m window, and the bed of the old river reads as a flat-bottomed trench. This adds real
surface relief: value-noise octaves down to 1.7 m, so there are hummocks, hollows and dips
you can see from standing height.

Steep ground is left alone (the noise weight fades out as slope rises), so the banks, cliffs
and the pond/swamp basins keep their shape.

Writes Zone1_Heightmap_v10.png + _RG.png and zone11_delta.npy for reseating props.
"""
import numpy as np
from PIL import Image

QUAD = 50.0
ORIGIN_X, ORIGIN_Y = -3000.0, -12600.0

X0, X1 = 38400.0, 49400.0      # NestingGrounds, the flattest zone in the level
FADE = 1200.0
YLIM, YFADE = 5600.0, 900.0

# (centre_x, centre_y, radius) - water basins whose beds must not move
WATER = [(26200.0, 0.0, 1650.0), (29700.0, 0.0, 2750.0)]

hm = np.asarray(Image.open("Zone1_Heightmap_v10.png")).astype(np.float64)
h = (hm - 32768) / 1.28
NY, NX = h.shape
X, Y = np.meshgrid(ORIGIN_X + QUAD * np.arange(NX), ORIGIN_Y + QUAD * np.arange(NY))


def smoothstep(e0, e1, v):
    t = np.clip((v - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def value_noise(wavelength_cm, seed):
    """Smooth random field. Organic lumps, unlike the sine products v7 used."""
    cells_x = max(2, int(NX * QUAD / wavelength_cm))
    cells_y = max(2, int(NY * QUAD / wavelength_cm))
    rng = np.random.default_rng(seed)
    g = rng.random((cells_y + 1, cells_x + 1)).astype(np.float32)
    img = Image.fromarray(g, mode="F").resize((NX, NY), Image.BICUBIC)
    a = np.asarray(img, dtype=np.float64)
    # normalise to unit standard deviation, so the amplitudes below mean real centimetres -
    # bicubic upsampling of white noise shrinks the spread badly otherwise
    return (a - a.mean()) / max(1e-9, a.std())


# long swell down to ruts underfoot - the short octaves are the ones that show
OCTAVES = [(2600.0, 12.0, 101), (1250.0, 10.0, 202), (640.0, 9.0, 303),
           (340.0, 6.0, 404), (170.0, 3.0, 505)]
noise = sum(amp * value_noise(wl, sd) for wl, amp, sd in OCTAVES)

# ---- where may it apply?
gy, gx = np.gradient(h, QUAD)
slope = np.hypot(gx, gy)
w = 1.0 - smoothstep(0.10, 0.28, slope)                       # leave banks and cliffs alone
w *= smoothstep(X0, X0 + FADE, X) * (1 - smoothstep(X1 - FADE, X1, X))
w *= smoothstep(-YLIM, -YLIM + YFADE, Y) * (1 - smoothstep(YLIM - YFADE, YLIM, Y))
for cx, cy, r in WATER:
    d = np.hypot(X - cx, Y - cy)
    w *= smoothstep(r - 450.0, r, d)                          # don't disturb the water beds

for _ in range(4):                                            # no step at the boundary
    w = 0.25 * (np.roll(w, 1, 0) + np.roll(w, -1, 0) + np.roll(w, 1, 1) + np.roll(w, -1, 1))
w = np.clip(w, 0.0, 1.0)

h_new = h + noise * w

out = np.clip(np.round(32768 + h_new * 1.28), 0, 65535).astype(np.uint16)
Image.fromarray(out).save("Zone1_Heightmap_v11.png")
rg = np.zeros((NY, NX, 4), np.uint8)
rg[..., 0] = out >> 8; rg[..., 1] = out & 255; rg[..., 3] = 255
Image.fromarray(rg, "RGBA").save("Zone1_Heightmap_v11_RG.png")

hq = (out.astype(np.float64) - 32768) / 1.28
np.save("zone11_delta.npy", hq - h)


def local_range(a, r=2):
    lo = a.copy(); hi = a.copy()
    for d in range(1, r + 1):
        for sh in (d, -d):
            lo = np.minimum(lo, np.roll(a, sh, 0)); lo = np.minimum(lo, np.roll(a, sh, 1))
            hi = np.maximum(hi, np.roll(a, sh, 0)); hi = np.maximum(hi, np.roll(a, sh, 1))
    return hi - lo


before, after = local_range(h), local_range(hq)
d = hq - h
gy2, gx2 = np.gradient(hq, QUAD)
for nm, a, b in [("NestingGrounds", 38900, 48900), ("RaptorZone", 37300, 38900),
                 ("RockfallZone", 48900, 51900)]:
    m = (X > a) & (X < b) & (np.abs(Y) < 1800)
    print(f"  {nm:<15} flat {100*(before[m]<6).mean():5.1f}% -> {100*(after[m]<6).mean():5.1f}%   "
          f"median relief {np.median(before[m]):5.1f} -> {np.median(after[m]):5.1f} cm")
print(f"\ndelta              : {d.min():+.0f} .. {d.max():+.0f} cm")
print(f"max slope anywhere : {100*np.hypot(gx2, gy2).max():.0f}%  "
      f"(corridor median {100*np.median(np.hypot(gx2,gy2)[(np.abs(Y)<1500)&(X>0)&(X<37000)]):.1f}%)")
for cx, cy, r in WATER:
    m = np.hypot(X - cx, Y - cy) < r - 450
    print(f"water basin ({cx:.0f},{cy:.0f}) moved: {np.abs(d[m]).max():.2f} cm")
print(f"changed outside the zone: {np.abs(d[(X < X0) | (X > X1)]).max():.2f} cm")
