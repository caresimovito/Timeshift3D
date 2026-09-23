"""Heightmap v8: break Zone 4's dead-flat ground into a field of basalt plates.

v5 carved the two lava rivers into the side basins but left the corridor you walk on
(|Y| < 1100) at exactly height 0, so the lava fields read as painted lino. The reference
look is a cracked crust: slabs a few metres across, each tilted a little, with the lava
sitting in the seams between them.

This lays a Worley cell field over x 77.5k-95.5k. Cell interiors rise and tilt; cell
boundaries drop into channels. The channels are what the material lights up - the lava
emissive keys off world Z, so glow can only ever appear in ground that is actually low.

Writes Zone1_Heightmap_v8.png + _RG.png (for Saved/import_land.py), zone4_basalt_delta.npy
so placed props can be nudged by the same amount the ground moved, and a hillshade preview.
"""
import numpy as np
from PIL import Image

QUAD = 50.0
ORIGIN_X, ORIGIN_Y = -3000.0, -12600.0

# zone footprint in world cm, with the fade band included
X0, X1 = 77500.0, 95500.0
Y0, Y1 = -5200.0, 5200.0
FADE_X, FADE_Y = 1800.0, 1100.0

PLATE_PX = 10          # ~5 m plates on the 50 cm grid
SEAM_PX = 3.0          # channel half-width, ~1.5 m
CHANNEL = 24.0         # cm the seams drop below the plate
PLATE_VAR = 7.0        # cm of plate-to-plate height variation
TILT_CM_PER_PX = 1.1   # each plate leans a little
RIVER_Z = -90.0        # don't touch anything already cut this low (the v5 lava rivers)

hm = np.asarray(Image.open("Zone1_Heightmap_v7.png")).astype(np.float64)
h = (hm - 32768) / 1.28
NY, NX = h.shape
X, Y = np.meshgrid(ORIGIN_X + QUAD * np.arange(NX), ORIGIN_Y + QUAD * np.arange(NY))


def smoothstep(e0, e1, v):
    t = np.clip((v - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


# ---- work on the zone sub-rectangle only
i0 = int((X0 - ORIGIN_X) / QUAD); i1 = int((X1 - ORIGIN_X) / QUAD)
j0 = int((Y0 - ORIGIN_Y) / QUAD); j1 = int((Y1 - ORIGIN_Y) / QUAD)
ny, nx = j1 - j0, i1 - i0
py, px = np.meshgrid(np.arange(ny), np.arange(nx), indexing="ij")

# ---- Worley cells: jittered seed grid, F1/F2 over the 3x3 neighbourhood
gy, gx = ny // PLATE_PX + 3, nx // PLATE_PX + 3
rng = np.random.default_rng(11)
jit = rng.random((gy, gx, 2)) * 0.8 + 0.1
pvar = (rng.random((gy, gx)) - 0.5) * 2.0 * PLATE_VAR
tilt = (rng.random((gy, gx, 2)) - 0.5) * 2.0 * TILT_CM_PER_PX

cj, ci = py // PLATE_PX + 1, px // PLATE_PX + 1
F1 = np.full((ny, nx), 1e9); F2 = np.full((ny, nx), 1e9)
B1j = np.zeros((ny, nx), np.int32); B1i = np.zeros((ny, nx), np.int32)
S1y = np.zeros((ny, nx)); S1x = np.zeros((ny, nx))
for dj in (-1, 0, 1):
    for di in (-1, 0, 1):
        nj, ni = cj + dj, ci + di
        sy = (nj - 1 + jit[nj, ni, 0]) * PLATE_PX
        sx = (ni - 1 + jit[nj, ni, 1]) * PLATE_PX
        d = np.hypot(py - sy, px - sx)
        closer = d < F1
        F2 = np.where(closer, F1, np.minimum(F2, d))
        B1j = np.where(closer, nj, B1j); B1i = np.where(closer, ni, B1i)
        S1y = np.where(closer, sy, S1y); S1x = np.where(closer, sx, S1x)
        F1 = np.where(closer, d, F1)

edge = F2 - F1                                   # 0 exactly on a seam
seam = 1.0 - smoothstep(0.0, SEAM_PX, edge)

plate = pvar[B1j, B1i]
plate += tilt[B1j, B1i, 0] * (py - S1y) + tilt[B1j, B1i, 1] * (px - S1x)

# broad swell so the field is not a uniform carpet of plates
xs, ys = X[j0:j1, i0:i1], Y[j0:j1, i0:i1]
swell = (32 * np.sin(xs / 2600.0 + 0.4) * np.sin(ys / 2100.0 - 0.7)
         + 17 * np.sin(xs / 1150.0 - 1.9) * np.sin(ys / 1400.0 + 2.2)
         + 8 * np.sin(xs / 520.0 + 3.1) * np.sin(ys / 610.0))

relief = plate + swell - CHANNEL * seam

# ---- fade to zero at the zone edge, and leave the v5 river beds alone
sub = h[j0:j1, i0:i1]
w = (smoothstep(X0, X0 + FADE_X, xs) * (1 - smoothstep(X1 - FADE_X, X1, xs))
     * smoothstep(Y0, Y0 + FADE_Y, ys) * (1 - smoothstep(Y1 - FADE_Y, Y1, ys)))
w *= smoothstep(RIVER_Z - 40, RIVER_Z + 40, sub)

h_new = h.copy()
h_new[j0:j1, i0:i1] = sub + relief * w

out = np.clip(np.round(32768 + h_new * 1.28), 0, 65535).astype(np.uint16)
Image.fromarray(out).save("Zone1_Heightmap_v8.png")
rg = np.zeros((NY, NX, 4), np.uint8)
rg[..., 0] = out >> 8; rg[..., 1] = out & 255; rg[..., 3] = 255
Image.fromarray(rg, "RGBA").save("Zone1_Heightmap_v8_RG.png")

hq = (out.astype(np.float64) - 32768) / 1.28
delta = hq - h
np.save("zone4_basalt_delta.npy", delta)

# ---- hillshade preview of the zone so the plate pattern can be eyeballed
z = hq[j0:j1, i0:i1]
gyy, gxx = np.gradient(z, QUAD)
shade = np.clip((1.6 - gxx * 2.4 - gyy * 1.1) / 3.2, 0, 1)
tint = np.clip((z - z.min()) / max(1e-6, float(z.max() - z.min())), 0, 1)
rgbp = np.zeros((ny, nx, 3), np.uint8)
rgbp[..., 0] = (shade * 90 + (1 - tint) * 150).clip(0, 255)
rgbp[..., 1] = (shade * 70 + (1 - tint) * 45).clip(0, 255)
rgbp[..., 2] = (shade * 65).clip(0, 255)
Image.fromarray(rgbp).resize((nx * 2, ny * 2), Image.NEAREST).save("Zone1_v8_preview.png")

slope = np.abs(np.gradient(z, QUAD)[0]) + np.abs(np.gradient(z, QUAD)[1])
print(f"zone cells reshaped : {(np.abs(delta) > 0.5).sum()}")
print(f"relief              : {z.min():.0f} .. {z.max():.0f} cm  (was flat at 0 on the corridor)")
print(f"delta               : {delta.min():.0f} .. {delta.max():.0f} cm")
print(f"max slope added     : {slope.max()*100:.1f} %   median {np.median(slope)*100:.1f} %")
print(f"changed outside zone: {(np.abs(delta[:j0]).max() if j0 else 0):.2f} / {(np.abs(delta[j1:]).max()):.2f} cm")
print(f"corridor |Y|<1100   : {z[(np.abs(ys[:,0])<1100)].min():.0f} .. {z[(np.abs(ys[:,0])<1100)].max():.0f} cm")
