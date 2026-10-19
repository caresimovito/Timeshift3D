# Generate rockfall sounds, 16-bit mono WAV:
#  S_RockRumble     - 2.6 s warning: deep growling rumble swelling up, with sharp rock cracks and trickling pebbles
#  S_RockImpact_01-3 - heavy boulder thud: low thump + crunchy gravel tail
import sys
import wave
import numpy as np

out_dir = sys.argv[1]
sr = 44100
rng = np.random.default_rng(23)


def lp(x, *ws):
    for w in ws:
        x = np.convolve(x, np.ones(w) / w, mode="same")
    return x


def write(name, sig):
    sig = sig / np.max(np.abs(sig)) * 0.85
    n = len(sig)
    sig *= np.minimum(1, np.minimum(np.arange(n) / (0.004 * sr), (n - np.arange(n)) / (0.06 * sr)))
    with wave.open("%s/%s.wav" % (out_dir, name), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sr)
        f.writeframes((sig * 32767).astype(np.int16).tobytes())
    print("wrote %s %.2fs" % (name, n / sr))


def crack(n, i0, dur, bright):
    out = np.zeros(n)
    m = min(n - i0, int(dur * sr))
    tt = np.arange(m) / sr
    nz = rng.standard_normal(m)
    out[i0:i0 + m] = (nz - lp(nz, 3) * (1 - bright)) * np.exp(-tt / (dur / 5))
    return out


# ---- rumble
d = 2.6
n = int(sr * d)
t = np.arange(n) / sr
noise = rng.standard_normal(n)
growl = lp(noise, 200, 200, 100) * 60                 # sub rumble
grind = lp(noise, 25, 25) * 6                          # grinding mid
wob = 1 + 0.5 * lp(rng.standard_normal(n), 3000, 3000) * 40
swell = np.minimum(1, (t / 1.6) ** 1.3) * (0.55 + 0.45 * np.exp(-np.maximum(0, t - 2.0) / 0.4))
sig = (growl + grind) * wob * swell
for _ in range(7):                                     # cracks
    sig += crack(n, int(rng.uniform(0.3, 2.3) * sr), rng.uniform(0.05, 0.12), 0.6) * rng.uniform(0.6, 1.4) * np.max(np.abs(growl))
for _ in range(60):                                    # pebble ticks
    sig += crack(n, int(rng.uniform(0.5, 2.5) * sr), 0.012, 1.0) * rng.uniform(0.1, 0.35) * np.max(np.abs(growl))
write("S_RockRumble", sig)

# ---- impacts
for k in range(3):
    d = 0.9 + 0.15 * k
    n = int(sr * d)
    t = np.arange(n) / sr
    f0 = 52 + 9 * k
    thump = np.sin(2 * np.pi * (f0 * t - 18 * t * t)) * np.exp(-t / 0.09)
    body = lp(rng.standard_normal(n), 40, 40) * 9 * np.exp(-t / 0.12)
    gravel = np.zeros(n)
    for _ in range(25 + 8 * k):
        gravel += crack(n, int(rng.uniform(0.01, 0.5) * sr * (0.4 + rng.random())), rng.uniform(0.008, 0.03), 0.8) * rng.uniform(0.05, 0.25)
    hit = crack(n, 0, 0.04, 0.5) * 0.9
    write("S_RockImpact_0%d" % (k + 1), thump * 1.2 + body + gravel * np.exp(-t / 0.35) + hit)
