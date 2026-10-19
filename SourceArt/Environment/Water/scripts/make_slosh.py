# Generate 3 short water-slosh/splash sounds (filtered noise + bubbly modulation), 16-bit mono WAV, for wading footsteps.
import sys
import wave
import numpy as np

out_dir = sys.argv[1]
sr = 44100
rng = np.random.default_rng(7)
for k in range(3):
    dur = 0.42 + 0.06 * k
    n = int(sr * dur)
    t = np.arange(n) / sr
    noise = rng.standard_normal(n)
    # low-pass via moving average chain (soft, watery), then a touch of high band for the "spray"
    lp = noise.copy()
    for w in (9, 7, 5):
        lp = np.convolve(lp, np.ones(w) / w, mode="same")
    hp = noise - np.convolve(noise, np.ones(3) / 3, mode="same")
    body = lp * 1.0 + hp * 0.12
    # bubbly amplitude modulation + slosh envelope (fast attack, two lumps)
    bub = 0.6 + 0.4 * np.sin(2 * np.pi * (18 + 6 * k) * t + rng.uniform(0, 6)) * np.sin(2 * np.pi * (5 + k) * t)
    env = (1 - np.exp(-t / 0.012)) * (np.exp(-t / (0.09 + 0.02 * k)) + 0.45 * np.exp(-((t - 0.16 - 0.03 * k) / 0.05) ** 2))
    sig = body * bub * env
    sig = sig / np.max(np.abs(sig)) * 0.7
    fade = np.minimum(1, (n - np.arange(n)) / (0.02 * sr))
    sig *= fade
    data = (sig * 32767).astype(np.int16)
    with wave.open("%s/S_WaterSlosh_0%d.wav" % (out_dir, k + 1), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sr)
        f.writeframes(data.tobytes())
    print("wrote S_WaterSlosh_0%d.wav %.2fs" % (k + 1, dur))
