"""Seamless dry cracked-mud textures (Voronoi plates): BaseColor, Normal, Roughness."""
import numpy as np
from PIL import Image
import os

OUT = os.path.dirname(os.path.abspath(__file__))
N = 1024
rng = np.random.default_rng(3)


def voronoi_f1f2(grid):
    """Periodic jittered-grid Voronoi: F1, F2 distances (px) and cell id. One point per grid cell."""
    cs = N / grid
    jit = rng.uniform(0.1, 0.9, (grid, grid, 2))
    yy, xx = np.mgrid[0:N, 0:N].astype(np.float32)
    ci, cj = (xx // cs).astype(int), (yy // cs).astype(int)
    f1 = np.full((N, N), 1e9, np.float32); f2 = np.full((N, N), 1e9, np.float32)
    idx = np.zeros((N, N), np.int32)
    for dj in range(-2, 3):
        for di in range(-2, 3):
            ni, nj = ci + di, cj + dj
            wi, wj = ni % grid, nj % grid
            px = (ni + jit[wj, wi, 0]) * cs
            py = (nj + jit[wj, wi, 1]) * cs
            d = np.sqrt((xx - px) ** 2 + (yy - py) ** 2)
            closer = d < f1
            f2 = np.where(closer, f1, np.minimum(f2, d))
            idx = np.where(closer, wj * grid + wi, idx)
            f1 = np.where(closer, d, f1)
    return f1, f2, idx


def noise(beta, kmin, kmax):
    k = np.sqrt(np.fft.fftfreq(N)[None, :] ** 2 + np.fft.fftfreq(N)[:, None] ** 2) * N
    amp = np.where((k >= kmin) & (k <= kmax), (k + 1e-6) ** (-beta), 0.0)
    f = np.real(np.fft.ifft2(amp * np.exp(1j * rng.uniform(0, 2 * np.pi, (N, N)))))
    return (f - f.mean()) / f.std()


f1, f2, cell = voronoi_f1f2(9)
edge = f2 - f1                      # 0 on a crack
warp = noise(1.8, 8, 120)
crack_w = 5.0 + 2.0 * warp          # varying crack width in px
crack = np.clip(1.0 - edge / np.maximum(crack_w, 1.5), 0, 1) ** 1.5   # 1 inside crack
# fine hairline cracks from a second, denser pattern
g1, g2, _ = voronoi_f1f2(20)
hair = np.clip(1.0 - (g2 - g1) / 1.2, 0, 1) * 0.22

# plate height: plates curl up slightly towards their edges, cracks are deep
plate = np.clip(edge / 40.0, 0, 1)
height = 0.6 + 0.25 * (1 - plate) * (1 - crack) - 0.9 * crack - 0.25 * hair + 0.05 * noise(1.5, 20, 300)

# base colour: pale sun-baked clay with per-plate tint variation, dark cracks
tint = (np.sin(cell * 12.9898) * 43758.5453) % 1.0
clay = np.stack([0.60, 0.45, 0.30])[None, None, :] * (0.88 + 0.16 * tint[..., None])
clay = clay * (0.92 + 0.08 * noise(1.6, 4, 200)[..., None])
dark = np.array([0.22, 0.16, 0.11])[None, None, :]
m = np.clip(crack + hair, 0, 1)[..., None]
bc = clay * (1 - m) + dark * m
Image.fromarray((np.clip(bc, 0, 1) ** (1 / 2.2) * 255).astype(np.uint8), 'RGB').save(os.path.join(OUT, 'T_CrackedMud_BC.png'))

gx = (np.roll(height, -1, 1) - np.roll(height, 1, 1)) * 0.5
gy = (np.roll(height, -1, 0) - np.roll(height, 1, 0)) * 0.5
s = 6.0
n = np.stack([-gx * s, -gy * s, np.ones_like(height)], -1)
n /= np.linalg.norm(n, axis=-1, keepdims=True)
Image.fromarray(((n * 0.5 + 0.5) * 255).round().astype(np.uint8), 'RGB').save(os.path.join(OUT, 'T_CrackedMud_N.png'))

rough = np.clip(0.85 + 0.1 * m[..., 0] + 0.03 * noise(1.5, 10, 200), 0, 1)
Image.fromarray((rough * 255).astype(np.uint8), 'L').convert('RGB').save(os.path.join(OUT, 'T_CrackedMud_R.png'))
print('ok')
