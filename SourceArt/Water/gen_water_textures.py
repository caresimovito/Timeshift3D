"""Generate seamless water textures: ripple normal map + slow noise mask (spectral synthesis, periodic)."""
import numpy as np
from PIL import Image
import os
OUT = os.path.dirname(os.path.abspath(__file__))
N = 1024
rng = np.random.default_rng(7)

def field(beta, kmin, kmax):
    kx = np.fft.fftfreq(N) * N
    ky = np.fft.fftfreq(N) * N
    k = np.sqrt(kx[None, :] ** 2 + ky[:, None] ** 2)
    amp = np.where((k >= kmin) & (k <= kmax), (k + 1e-6) ** (-beta), 0.0)
    ph = rng.uniform(0, 2 * np.pi, (N, N))
    f = np.real(np.fft.ifft2(amp * np.exp(1j * ph)))
    return (f - f.mean()) / f.std()

# ripples: mix of small wavelets
h = field(1.9, 14, 90)
gx = (np.roll(h, -1, 1) - np.roll(h, 1, 1)) * 0.5
gy = (np.roll(h, -1, 0) - np.roll(h, 1, 0)) * 0.5
s = 4.0
n = np.stack([-gx * s, -gy * s, np.ones_like(h)], -1)
n /= np.linalg.norm(n, axis=-1, keepdims=True)
Image.fromarray(((n * 0.5 + 0.5) * 255).round().astype(np.uint8), 'RGB').save(os.path.join(OUT, 'T_Water_Ripple_N.png'))

# scum / variation mask: low frequency blobs
m = field(2.4, 2, 24)
m = (m - m.min()) / (m.max() - m.min())
Image.fromarray((m * 255).round().astype(np.uint8), 'L').convert('RGB').save(os.path.join(OUT, 'T_Water_Noise.png'))
print('ok', n[..., 2].min())
