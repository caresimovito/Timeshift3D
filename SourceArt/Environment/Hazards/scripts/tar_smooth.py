"""Smooth, organic tar pool outline (user 2026-10-22: "too straight edges, doesn't look real").

SM_TarPit was built from 1 m cells (build_tar_mesh.py: tar_cells.json grown by one cell), so its edge was a staircase of
straight lines. This keeps the same footprint and centre but blurs the cell mask (Gaussian, sigma 0.9 m), adds a gentle
low-frequency wobble so the edge is irregular rather than a rounded rectangle, and contours it at 0.5 with MARCHING
SQUARES on a 25 cm grid - a smooth curved shoreline. Output C:/agentpy/tar_smooth.json (verts relative to the old mesh
centre, faces, uv) for tar_smooth_fbx.py. UVs are planar at the old mesh's scale (2200 cm = 1 UV unit).
"""
import json
import math
import random

d = json.load(open(r"C:/agentpy/tar_cells.json"))
C = d["cell"]
mx = min(x for x, _ in d["cells"])
my = min(y for _, y in d["cells"])
cells = {(round((x - mx) / C), round((y - my) / C)) for x, y in d["cells"]}
grown = set(cells)
for (i, j) in cells:
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            grown.add((i + di, j + dj))
ii = [i for i, _ in grown]
jj = [j for _, j in grown]
ci, cj = (min(ii) + max(ii)) / 2, (min(jj) + max(jj)) / 2
CX, CY = mx + ci * C, my + cj * C                          # old mesh origin (world) - the actor sits here
pts = [((i - ci) * C, (j - cj) * C) for i, j in grown]     # cell centres, mesh-local

SIG = 90.0
NORM = sum(math.exp(-((a * C) ** 2 + (b * C) ** 2) / (2 * SIG * SIG)) for a in range(-6, 7) for b in range(-6, 7))
rnd = random.Random(7)
waves = [(rnd.uniform(0, 2 * math.pi), rnd.uniform(0, 2 * math.pi), 2 * math.pi / rnd.uniform(300, 650), 0.07) for _ in range(5)]


def field(x, y):
    f = 0.0
    for px, py in pts:
        dx, dy = x - px, y - py
        if abs(dx) < 4 * SIG and abs(dy) < 4 * SIG:
            f += math.exp(-(dx * dx + dy * dy) / (2 * SIG * SIG))
    f /= NORM
    for ph, ang, k, amp in waves:                          # wobble: a few soft ripples in random directions
        f += amp * math.sin(k * (x * math.cos(ang) + y * math.sin(ang)) + ph)
    return f


S = 25.0
xs = [min(p[0] for p in pts) - 200 + S * k for k in range(int((max(p[0] for p in pts) - min(p[0] for p in pts) + 400) / S) + 1)]
ys = [min(p[1] for p in pts) - 200 + S * k for k in range(int((max(p[1] for p in pts) - min(p[1] for p in pts) + 400) / S) + 1)]
F = [[0.5 - field(x, y) for x in xs] for y in ys]            # < 0 = tar
verts, vid, faces = [], {}, []


def V(x, y):
    key = (round(x, 1), round(y, 1))
    if key not in vid:
        vid[key] = len(verts)
        verts.append(key)
    return vid[key]


for iy in range(len(ys) - 1):
    for ix in range(len(xs) - 1):
        corners = [(ix, iy), (ix + 1, iy), (ix + 1, iy + 1), (ix, iy + 1)]
        vals = [F[b][a] for a, b in corners]
        if all(v >= 0 for v in vals):
            continue
        poly = []
        for k in range(4):
            (a0, b0), (a1, b1) = corners[k], corners[(k + 1) % 4]
            v0, v1 = vals[k], vals[(k + 1) % 4]
            if v0 < 0:
                poly.append((xs[a0], ys[b0]))
            if (v0 < 0) != (v1 < 0):
                t = v0 / (v0 - v1)
                poly.append((xs[a0] + (xs[a1] - xs[a0]) * t, ys[b0] + (ys[b1] - ys[b0]) * t))
        if len(poly) < 3:
            continue
        ids = [V(x, y) for x, y in poly]
        if len(ids) == 6 and sum(1 for v in vals if v < 0) == 2:
            faces.append((ids[0], ids[1], ids[5]))
            faces.append((ids[2], ids[3], ids[4]))
            continue
        for k in range(1, len(ids) - 1):
            faces.append((ids[0], ids[k], ids[k + 1]))

uv = [((x + 1100.0) / 2200.0, (y + 1000.0) / 2200.0) for x, y in verts]
json.dump({"centre": [CX, CY], "verts": verts, "faces": faces, "uv": uv}, open(r"C:/agentpy/tar_smooth.json", "w"))
vx = [v[0] for v in verts]
vy = [v[1] for v in verts]
area = sum(abs((verts[b][0] - verts[a][0]) * (verts[c][1] - verts[a][1]) - (verts[c][0] - verts[a][0]) * (verts[b][1] - verts[a][1])) / 2
           for a, b, c in faces) / 1e4
print("[TARS] cells %d grown %d | centre (%.1f, %.1f) | verts %d tris %d | box x %.0f..%.0f y %.0f..%.0f | area %.0f m2 (old %d m2)" % (
    len(cells), len(grown), CX, CY, len(verts), len(faces), min(vx), max(vx), min(vy), max(vy), area, len(grown)))
