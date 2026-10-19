# Generate geyser sounds, 16-bit mono WAV:
#  S_GeyserHiss  - 1.8 s warning: gurgling bubbles under a hiss that swells toward the burst
#  S_GeyserBurst - 3.2 s eruption: sharp whoosh onset, roaring broadband steam + low rumble, slow decay
import sys
import wave
import numpy as np

out_dir = sys.argv[1]
sr = 44100
rng = np.random.default_rng(11)


def lp(x, *ws):
    for w in ws:
        x = np.convolve(x, np.ones(w) / w, mode="same")
    return x


def write(name, sig):
    sig = sig / np.max(np.abs(sig)) * 0.8
    n = len(sig)
    sig *= np.minimum(1, np.minimum(np.arange(n) / (0.005 * sr), (n - np.arange(n)) / (0.08 * sr)))
    with wave.open("%s/%s.wav" % (out_dir, name), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sr)
        f.writeframes((sig * 32767).astype(np.int16).tobytes())
    print("wrote %s %.2fs" % (name, n / sr))


# ---- hiss + gurgle
d = 1.8
n = int(sr * d)
t = np.arange(n) / sr
noise = rng.standard_normal(n)
hiss = noise - lp(noise, 4)                       # bright hiss
swell = (t / d) ** 1.6
gurgle = np.zeros(n)
for _ in range(38):                                # bubbles: short decaying chirps, denser near the end
    t0 = d * rng.random() ** 0.6
    f0 = rng.uniform(180, 520)
    i0 = int(t0 * sr)
    m = min(n - i0, int(0.06 * sr))
    tt = np.arange(m) / sr
    gurgle[i0:i0 + m] += np.sin(2 * np.pi * (f0 * tt + 900 * tt * tt)) * np.exp(-tt / 0.018)
write("S_GeyserHiss", hiss * (0.15 + 0.85 * swell) * 0.5 + gurgle * 0.35 + lp(noise, 30, 30) * 2.0 * swell)

# ---- burst
d = 3.2
n = int(sr * d)
t = np.arange(n) / sr
noise = rng.standard_normal(n)
roar = lp(noise, 3) * 0.7 + (noise - lp(noise, 6)) * 0.35          # broadband steam
rumble = lp(noise, 120, 120, 60) * 40                                # low body
env = (1 - np.exp(-t / 0.03)) * (0.35 + 0.65 * np.exp(-t / 1.4))
flutter = 1 + 0.25 * lp(rng.standard_normal(n), 2000, 2000) * 30     # turbulent wobble
whoosh = np.exp(-t / 0.12) * (noise - lp(noise, 2)) * 0.8             # onset crack
write("S_GeyserBurst", (roar * flutter + rumble) * env + whoosh)
