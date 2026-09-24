"""Build the camera path for the Chronoshift trailer.

Each shot is a start and end pose plus a duration; positions and rotations are eased so the
camera glides rather than snapping. Heights are taken from the live heightmap so the camera
holds a constant distance above the ground instead of clipping through hills.
"""
import json
import numpy as np
from PIL import Image

FPS = 30
QUAD, OX, OY = 50.0, -3000.0, -12600.0
h = (np.asarray(Image.open(r"C:/repos/Unreal Projects/Timeshift3D/SourceArt/Landscape/Zone1_Heightmap_v11.png")).astype(np.float64) - 32768) / 1.28
NY, NX = h.shape


def ground(x, y):
    i = max(0, min(NX - 1, int(round((x - OX) / QUAD))))
    j = max(0, min(NY - 1, int(round((y - OY) / QUAD))))
    return float(h[j, i])


def ease(t):
    return t * t * (3 - 2 * t)


# (name, seconds, start xyz + above-ground height, end xyz, start pitch/yaw, end pitch/yaw)
SHOTS = [
    # opens over the hero's shoulder at the player start, looking out into the era
    # the hero walks east out of the arrival grove at 500 cm/s; camera tracks 4.5 m behind.
    # marked linear so the camera holds station instead of easing away from him.
    ('walk',     8.0, (-450, 105, 205), (3550, 105, 195), (-5,  0), (-5,  0), 12.0, 'linear'),
    ('arrival',  5.0, (1200,  600, 220), (4200,  200, 200), (-4,  -8), (-2,  6), 12.2),
    ('meadow',   5.0, (13200, -900, 260), (16800, 400, 230), (-3, 14), (-5, -6), 11.4),
    ('pond',     4.5, (24600, 1400, 300), (27200, 300, 240), (-8, -22), (-4, 4), 11.4),
    ('swamp',    4.0, (29000, -1500, 280), (31200, 600, 250), (-5, 26), (-3, -8), 11.6),
    ('nesting',  6.0, (40200, 300, 250), (44600, -80, 230), (-2, -2), (0, 2), 11.4),
    ('canyon',   4.5, (54500, 200, 260), (58500, -150, 240), (-2, -1), (-1, 2), 11.6),
    ('ashforest',4.0, (69500, 700, 280), (72800, -300, 250), (-3, -9), (-2, 5), 11.2),
    ('lava',     5.5, (81500, 900, 300), (86500, -200, 260), (-4, -10), (-6, 3), 10.0),
    ('arena',    6.0, (92800, 1600, 420), (95000, 250, 300), (-5, -18), (-8, -3), 10.6),
]

import sys
if len(sys.argv) > 1 and sys.argv[1] in ('hero-only', 'walk-only'):
    SHOTS = [x for x in SHOTS if x[0] == 'walk']

frames = []
for shot in SHOTS:
    name, secs, a, b, ra, rb, bias = shot[:7]
    linear = len(shot) > 7 and shot[7] == 'linear'
    n = int(secs * FPS)
    for k in range(n):
        u = k / max(1, n - 1)
        t = u if linear else ease(u)
        x = a[0] + (b[0] - a[0]) * t
        y = a[1] + (b[1] - a[1]) * t
        above = a[2] + (b[2] - a[2]) * t
        pitch = ra[0] + (rb[0] - ra[0]) * t
        yaw = ra[1] + (rb[1] - ra[1]) * t
        frames.append({'shot': name, 'bias': bias,
                       'loc': [round(x, 1), round(y, 1), round(ground(x, y) + above, 1)],
                       'rot': [round(pitch, 2), round(yaw, 2), 0.0]})

json.dump({'fps': FPS, 'frames': frames},
          open(r"C:/repos/Unreal Projects/Timeshift3D/Saved/trailer_path.json", "w"))
print(f"shots   : {len(SHOTS)}")
print(f"frames  : {len(frames)}  ({len(frames)/FPS:.1f} s at {FPS} fps)")
for shot in SHOTS:
    print(f"   {shot[0]:<10} {shot[1]:>4.1f} s" + ('   linear' if len(shot) > 7 else ''))
