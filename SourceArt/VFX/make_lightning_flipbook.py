# Procedural lightning-bolt flipbook for the Adrenaline power-up (user 2026-10-23 picked Grok concept 4: blue-white
# lightning crackling between his feet and the ground + a thin electric trail). 4x4 frames, 512 px -> 2048 RGBA PNG.
# Each frame = a different jagged bolt (midpoint displacement) running bottom -> top with 1-3 side branches.
# RGB = white core, A = core + soft glow. Colour comes from the material / particle colour.
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFilter

N, F = 512, 4
rng = np.random.default_rng(11)

def bolt(p0, p1, rough, depth):
    pts = [np.array(p0, float), np.array(p1, float)]
    for d in range(depth):
        new = [pts[0]]
        for a, b in zip(pts[:-1], pts[1:]):
            m = (a + b) / 2
            seg = b - a
            nrm = np.array([-seg[1], seg[0]]) / (np.linalg.norm(seg) + 1e-6)
            m = m + nrm * rng.normal(0, rough * np.linalg.norm(seg))
            new += [m, b]
        pts = new
    return pts

sheet = np.zeros((N * F, N * F, 4), np.float32)
for i in range(F * F):
    core = Image.new("L", (N, N), 0)
    d = ImageDraw.Draw(core)
    x0 = N / 2 + rng.normal(0, 30)
    main = bolt((x0, N - 20), (N / 2 + rng.normal(0, 90), 20), 0.22, 7)
    d.line([tuple(p) for p in main], fill=255, width=5)
    for _ in range(rng.integers(1, 4)):
        k = rng.integers(len(main) // 5, len(main) * 3 // 4)
        s = main[k]
        e = s + np.array([rng.normal(0, 140), -rng.uniform(60, 200)])
        br = bolt(s, e, 0.25, 5)
        d.line([tuple(p) for p in br], fill=200, width=3)
    c = np.asarray(core, np.float32) / 255
    glow = np.asarray(core.filter(ImageFilter.GaussianBlur(10)), np.float32) / 255
    halo = np.asarray(core.filter(ImageFilter.GaussianBlur(28)), np.float32) / 255
    a = np.clip(c + glow * 1.6 + halo * 1.2, 0, 1)
    rgb = np.clip(c + glow * 0.9, 0, 1)
    r, col = divmod(i, F)
    sheet[r*N:(r+1)*N, col*N:(col+1)*N] = np.stack([rgb, rgb, rgb, a], -1)
out = sys.argv[1] if len(sys.argv) > 1 else "T_Lightning_4x4.png"
Image.fromarray((sheet * 255).astype(np.uint8), "RGBA").save(out)
prev = sheet[0:N, 0:4 * N]
blue = np.stack([prev[..., 3] * 0.35 + prev[..., 0] * 0.65, prev[..., 3] * 0.55 + prev[..., 0] * 0.45, prev[..., 3]], -1)
Image.fromarray((np.clip(blue, 0, 1) * 255).astype(np.uint8), "RGB").resize((1024, 256)).save(out.replace(".png", "_preview.png"))
print("ok", out)
