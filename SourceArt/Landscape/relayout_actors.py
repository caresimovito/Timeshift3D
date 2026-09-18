"""Compute new transforms for existing actors after moving to the extended layout.

Reads Saved/relayout_actors.json (exported from the editor), maps each actor's X
from the old 150 m layout to the new one (zone_layout.json), keeps Y, and shifts
Z by the difference between the old and new terrain at that spot.
Writes Saved/relayout_moves.json for the editor to apply.
"""
import json
import numpy as np
from PIL import Image

ROOT = "C:/repos/Unreal Projects/Timeshift3D/"
layout = json.load(open(ROOT + "SourceArt/Landscape/zone_layout.json"))
actors = json.load(open(ROOT + "Saved/relayout_actors.json"))

old_h = (np.asarray(Image.open(ROOT + "SourceArt/Landscape/Zone1_Heightmap.png")).astype(float) - 32768) / 1.28
new_h = (np.asarray(Image.open(ROOT + "SourceArt/Landscape/Zone1_Heightmap_v2.png")).astype(float) - 32768) / 1.28


def sample(h, ox, oy, x, y):
    i = (x - ox) / 50.0
    j = (y - oy) / 50.0
    if not (0 <= i < h.shape[1] - 1 and 0 <= j < h.shape[0] - 1):
        return None
    i0, j0 = int(i), int(j)
    fi, fj = i - i0, j - j0
    return (h[j0, i0] * (1 - fi) * (1 - fj) + h[j0, i0 + 1] * fi * (1 - fj)
            + h[j0 + 1, i0] * (1 - fi) * fj + h[j0 + 1, i0 + 1] * fi * fj)


def map_x(x):
    for o0, o1, n0, n1 in layout["x_map_old_to_new"]:
        if o0 <= x < o1:
            if n0 is None:
                return x if o0 < 0 else x + 82400, 1.0
            k = (n1 - n0) / (o1 - o0)
            return n0 + (x - o0) * k, k
    return x, 1.0


BACKGROUND = {  # huge backdrop meshes: spread along the new length instead of mapping
    (3000, 17000): (25000, 17000), (3000, -17000): (25000, -17000),
    (11000, 17500): (70000, 17500), (11000, -17500): (70000, -17500),
    (27500, 0): (118000, 0),
}

moves = []
for a in actors:
    xf = a["xf"]
    loc, scale = xf["location"], xf["scale"]
    x, y, z = loc["x"], loc["y"], loc["z"]
    cls = a["cls"]
    if cls == "PCGVolume":
        moves.append({"path": a["path"], "xf": {"location": {"x": 52125, "y": 0, "z": 2500}, "rotation": xf["rotation"],
                                                 "scale": {"x": 551.25, "y": 126, "z": 60}}})
        continue
    if scale["x"] >= 50:
        key = (round(x), round(y))
        if key in BACKGROUND:
            nx, ny = BACKGROUND[key]
            moves.append({"path": a["path"], "xf": {"location": {"x": nx, "y": ny, "z": z}, "rotation": xf["rotation"], "scale": scale}})
        continue
    nx, k = map_x(x)
    nz = z
    if z > -1000:  # skip the deep bridge collision block
        ho = sample(old_h, -3000, -9450, x, y)
        hn = sample(new_h, -3000, -12600, nx, y)
        if ho is not None and hn is not None:
            nz = z + (hn - ho)
    new_scale = dict(scale)
    if cls == "LocalFogVolume" and k > 1:
        new_scale["x"] = min(scale["x"] * k, scale["x"] * 3)
    if abs(nx - x) < 0.5 and abs(nz - z) < 0.5 and new_scale == scale:
        continue
    moves.append({"path": a["path"], "xf": {"location": {"x": round(nx, 1), "y": y, "z": round(nz, 1)},
                                             "rotation": xf["rotation"], "scale": new_scale}})

json.dump(moves, open(ROOT + "Saved/relayout_moves.json", "w"))
print(f"{len(actors)} actors, {len(moves)} to move")
big = [m for m in moves if abs(m["xf"]["location"]["z"] - next(a["xf"]["location"]["z"] for a in actors if a["path"] == m["path"])) > 200]
print(f"{len(big)} with a Z change over 2 m")
