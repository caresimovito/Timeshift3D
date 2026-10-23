# Procedural looping flame-tongue flipbook for the Fury power-up (no source artwork).
# 8x8 frames, 256 px each -> 2048x2048 RGBA PNG.
#   R = heat (1 = white-hot core, falls off to the tips), A = flame mask.
# Shape: teardrop that narrows with height, edges eaten by 3D value noise scrolling upward.
# The noise's time axis runs around a circle, so frame 63 -> frame 0 loops seamlessly.
import sys, numpy as np
from PIL import Image

N, F = 256, 8
rng = np.random.default_rng(7)
G = 32
lat = rng.random((G, G, G)).astype(np.float32)

def vnoise(x, y, z):
    # trilinear value noise on a periodic lattice
    xi, yi, zi = np.floor(x).astype(int), np.floor(y).astype(int), np.floor(z).astype(int)
    xf, yf, zf = x - xi, y - yi, z - zi
    s = lambda t: t * t * (3 - 2 * t)
    u, v, w = s(xf), s(yf), s(zf)
    def L(dx, dy, dz):
        return lat[(xi + dx) % G, (yi + dy) % G, (zi + dz) % G]
    c00 = L(0,0,0)*(1-u) + L(1,0,0)*u; c10 = L(0,1,0)*(1-u) + L(1,1,0)*u
    c01 = L(0,0,1)*(1-u) + L(1,0,1)*u; c11 = L(0,1,1)*(1-u) + L(1,1,1)*u
    return (c00*(1-v) + c10*v)*(1-w) + (c01*(1-v) + c11*v)*w

def fbm(x, y, z, oct=4):
    a, t, f = 0.5, 0.0, 1.0
    for _ in range(oct):
        t += a * vnoise(x * f, y * f, z * f); a *= 0.5; f *= 2.0
    return t

ys, xs = np.mgrid[0:N, 0:N].astype(np.float32) / N   # ys: 0 top .. 1 bottom
h = 1.0 - ys                                          # height above the base
cx = xs - 0.5
sheet = np.zeros((N * F, N * F, 4), np.float32)
for i in range(F * F):
    ang = 2 * np.pi * i / (F * F)
    tz = 4.0 + 3.0 * np.cos(ang); tw = 3.0 * np.sin(ang)      # loop in time
    # upward scroll: sample noise lower down as time advances
    n = fbm(xs * 5.0 + tw, (ys + 0.0) * 5.0 + tz * 1.6, tz + tw)
    n2 = fbm(xs * 11.0 - tw, ys * 9.0 + tz * 3.0, tw * 2.0 + 9.0, 3)
    # sideways lick: bend the column with height (two scales of wobble)
    n3 = fbm(xs * 3.0 + 17.0, ys * 7.0 + tz * 2.2, tw * 1.5 + 4.0, 3)
    bend = (n - 0.5) * 0.30 * h ** 1.2 + (n3 - 0.5) * 0.18 * h ** 2
    width = 0.20 * np.clip(1.0 - h / 0.92, 0, 1) ** 0.75 + 0.005   # teardrop: wide base, sharp tip at 92%
    d = np.abs(cx - bend) / width
    core = np.clip(1.0 - d, 0, 1)
    base = np.clip((h - 0.03) / 0.12, 0, 1)                     # soft bottom
    v = core * (0.55 + n2) * base - 0.38 * h                     # edges eaten more toward the top -> tongues
    mask = np.clip(v / 0.22, 0, 1)
    mask = mask * mask * (3 - 2 * mask)
    heat = np.clip(mask * np.sqrt(core) * (1.15 - h * 1.25), 0, 1) ** 1.3
    fr = np.stack([heat, heat, heat, mask], -1)
    r, c = divmod(i, F)
    sheet[r*N:(r+1)*N, c*N:(c+1)*N] = fr
out = sys.argv[1] if len(sys.argv) > 1 else "T_FuryFlame_8x8.png"
Image.fromarray((sheet * 255).astype(np.uint8), "RGBA").save(out)
# preview: first 4 frames coloured like the material will
prev = sheet[0:N, 0:4*N]
heat, a = prev[..., 0], prev[..., 3]
col = np.stack([np.clip(heat*3, 0, 1), np.clip(heat*1.6-0.2, 0, 1), np.clip(heat*2-1.2, 0, 1)], -1) * a[..., None]
Image.fromarray((col * 255).astype(np.uint8), "RGB").save(out.replace(".png", "_preview.png"))
print("ok", out)
