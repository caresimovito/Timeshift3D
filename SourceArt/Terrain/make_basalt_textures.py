"""Generate the tiling basalt-crust texture set for Zone 4's lava fields.

The landscape grid is 50 cm, so sculpting can only give the big plates and channels - the
crack detail that makes cooled lava read as rock has to live in the material. This builds a
seamless set from a two-octave Worley cell field: broad plates about 1.6 m across, with finer
chips inside them.

  T_Basalt_BaseColor  near-black basalt, ash dusting on the plate tops, darker in the seams
  T_Basalt_Normal     crack relief, the thing that actually catches the light
  T_Basalt_Mask       R = roughness, G = crack depth (drives the lava emissive)
"""
import numpy as np
from PIL import Image

N = 1024
TILE_M = 8.0          # world size one tile covers


def worley(cells, seed, warp=0.0, warp_seed=0):
    """Periodic Worley. Returns F1 and F2 in units of one cell.

    `warp` pushes the sample point around with periodic noise before the lookup, which is
    what stops the plates coming out as a tidy honeycomb."""
    rng = np.random.default_rng(seed)
    pts = (rng.random((cells, cells, 2)) * 0.74 + 0.13)
    step = N / cells
    yy, xx = np.meshgrid(np.arange(N), np.arange(N), indexing="ij")
    if warp > 0:
        yy = yy + (fbm(3, warp_seed, 2) - 0.5) * 2 * warp * step
        xx = xx + (fbm(3, warp_seed + 101, 2) - 0.5) * 2 * warp * step
        yy = yy % N; xx = xx % N
    cy, cx = (yy // step).astype(int) % cells, (xx // step).astype(int) % cells
    F1 = np.full((N, N), 1e9); F2 = np.full((N, N), 1e9)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            ny, nx = (cy + dy) % cells, (cx + dx) % cells
            sy = (cy + dy + pts[ny, nx, 0]) * step
            sx = (cx + dx + pts[ny, nx, 1]) * step
            d = np.hypot(yy - sy, xx - sx) / step
            F2 = np.minimum(F2, np.maximum(F1, d))
            F1 = np.minimum(F1, d)
    return F1, F2


def fbm(octaves, seed, base=3):
    """Periodic value noise - integer frequencies so it wraps at the tile edge."""
    rng = np.random.default_rng(seed)
    yy, xx = np.meshgrid(np.linspace(0, 2 * np.pi, N, endpoint=False),
                         np.linspace(0, 2 * np.pi, N, endpoint=False), indexing="ij")
    out = np.zeros((N, N)); amp = 1.0; tot = 0.0
    for o in range(octaves):
        f = base * 2 ** o
        for _ in range(3):
            a, b = rng.integers(1, f + 1, 2)
            ph, qh = rng.random(2) * 2 * np.pi
            sgn = 1 if rng.random() > 0.5 else -1
            out += amp * np.sin(a * yy + ph) * np.sin(sgn * b * xx + qh)
        tot += amp * 3; amp *= 0.5
    return (out / tot + 1) * 0.5


def crack(cells, seed, width, warp=0.0, warp_seed=0):
    f1, f2 = worley(cells, seed, warp, warp_seed)
    return np.clip(1.0 - (f2 - f1) / width, 0, 1) ** 2.1


coarse = crack(5, 3, 0.115, warp=0.33, warp_seed=71)    # the plate seams
fine = crack(13, 17, 0.085, warp=0.28, warp_seed=83)    # chips inside each plate
grain = fbm(4, 29)

# ---- height: seams cut deep, chips shallow, plates gently domed
height = -(1.00 * coarse + 0.34 * fine) + 0.10 * grain
height += 0.06 * (1.0 - coarse)                       # plate tops bulge a touch
height = (height - height.min()) / (height.max() - height.min())

# ---- normal, with the vertical scale that makes the cracks catch light
STRENGTH = 5.5
gy, gx = np.gradient(height * STRENGTH)
nz = np.ones_like(gx)
ln = np.sqrt(gx ** 2 + gy ** 2 + nz ** 2)
nrm = np.stack([(-gx / ln * 0.5 + 0.5), (gy / ln * 0.5 + 0.5), (nz / ln * 0.5 + 0.5)], -1)
Image.fromarray((nrm * 255).astype(np.uint8)).save("T_Basalt_Normal.png")

# ---- base colour: black basalt, pale ash settled on the flats, seams near-black
seam = np.clip(coarse + 0.45 * fine, 0, 1)
ash = np.clip((grain - 0.42) * 2.3, 0, 1) * (1.0 - seam) ** 2
base = np.zeros((N, N, 3))
base[..., 0] = 0.026 + 0.011 * grain
base[..., 1] = 0.023 + 0.010 * grain
base[..., 2] = 0.024 + 0.011 * grain
base *= (1.0 - 0.72 * seam)[..., None]                      # seams swallow the light
base += (ash * 0.055)[..., None] * np.array([1.00, 0.94, 0.88])
srgb = np.clip(base, 0, 1) ** (1 / 2.2)
Image.fromarray((srgb * 255).astype(np.uint8)).save("T_Basalt_BaseColor.png")

# ---- mask: R roughness, G crack depth for the lava emissive
rough = 0.94 - 0.22 * (1.0 - seam) * np.clip(grain * 1.4, 0, 1)
# Most of the crust has gone cold. Only the stretches where the broad heat field is high
# still glow, so the veins break up and fade instead of lighting the whole net evenly.
heat = fbm(3, 47, 2)
heat = np.clip((heat - 0.44) * 3.0, 0, 1)
glow = np.clip(coarse * 1.3 - 0.30, 0, 1) ** 1.2 * heat
mask = np.zeros((N, N, 3))
mask[..., 0] = np.clip(rough, 0, 1)
mask[..., 1] = glow
Image.fromarray((mask * 255).astype(np.uint8)).save("T_Basalt_Mask.png")

print(f"tile {N}px = {TILE_M} m  ->  {TILE_M*100/N:.2f} cm/px")
print(f"plates ~{TILE_M/5:.2f} m, chips ~{TILE_M/13:.2f} m")
print(f"seam coverage {100*(coarse>0.5).mean():.1f}%   glow coverage {100*(glow>0.35).mean():.1f}%")
