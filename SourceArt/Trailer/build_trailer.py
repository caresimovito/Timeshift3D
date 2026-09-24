"""Grade the rendered frames per shot and encode the trailer.

SceneCapture2D renders darker than the viewport but clips nothing, so each shot is lifted with
a gain/gamma pass sized from its own measured brightness rather than a single global curve.
"""
import json
import subprocess
import sys
import numpy as np
from PIL import Image

FRAMES = r"C:/repos/Unreal Projects/Timeshift3D/Saved/TrailerFrames"
GRADED = r"C:/repos/Unreal Projects/Timeshift3D/Saved/TrailerGraded"
OUT = r"C:/repos/Unreal Projects/Timeshift3D/Trailer_Chronoshift.mp4"
PATH = r"C:/repos/Unreal Projects/Timeshift3D/Saved/trailer_path.json"
TARGET = 96.0          # mean luma to aim each shot at
import os
os.makedirs(GRADED, exist_ok=True)
for f in os.listdir(GRADED):
    if f.endswith('.png'):
        os.remove(os.path.join(GRADED, f))

frames = json.load(open(PATH))['frames']
fps = json.load(open(PATH))['fps']

# measure one frame per shot to size that shot's lift
shots, seen = {}, []
for i, fr in enumerate(frames):
    shots.setdefault(fr['shot'], []).append(i)

gain = {}
for shot, idx in shots.items():
    mid = idx[len(idx) // 2]
    a = np.asarray(Image.open(f"{FRAMES}/f{mid:05d}.png").convert('RGB')).astype(np.float64)
    m = max(1.0, a.mean())
    g = min(6.0, TARGET / m)
    gain[shot] = g
    print(f"{shot:<10} mean {m:6.1f}  ->  gain {g:.2f}")

for i, fr in enumerate(frames):
    a = np.asarray(Image.open(f"{FRAMES}/f{i:05d}.png").convert('RGB')).astype(np.float64) / 255.0
    g = gain[fr['shot']]
    a = np.clip(a * g, 0, 1) ** 0.92            # lift, then a gentle gamma for the shadows
    Image.fromarray((a * 255).astype(np.uint8)).save(f"{GRADED}/g{i:05d}.png")
    if i % 200 == 0:
        print('graded', i)

cmd = ['ffmpeg', '-y', '-framerate', str(fps), '-i', f'{GRADED}/g%05d.png',
       '-c:v', 'libx264', '-preset', 'slow', '-crf', '18',
       '-pix_fmt', 'yuv420p', '-movflags', '+faststart', OUT]
print(' '.join(cmd))
subprocess.run(cmd, check=True)
print('wrote', OUT)
