"""Smooth swamp water surface (user 2026-10-21: "water looks way too angular").

The swamp water was built from 1 m cells (build_pond_mesh.py): wherever the ground sits near the water level the shore
showed the cell steps. This builds the surface from the landscape's own 50 cm height grid (heights.bin from
landscape_export_heights.py) with MARCHING SQUARES: each landscape quad contributes exactly the part that lies below
LEVEL (water surface + TUCK cm), with the shoreline interpolated along the quad edges - so the water edge follows the
terrain's own contour and tucks just under it. Region = below-level vertices flood-filled (8-connected) from the cells
the current water covers, limited to the old pond box (+6 m), so separate low ground elsewhere is not flooded.
Output: C:/agentpy/swamp_water_smooth.json (verts relative to the centre, faces, centre, surface z) for Blender.
"""
import array
import json
from collections import deque

M = json.load(open(r"C:/agentpy/heights_meta.json"))
W, H = M["width"], M["height"]
MINX, MINY, SC = M["min_x"], M["min_y"], M["scale"][0]
CMU, MID = M["cm_per_unit"], M["mid"]
hts = array.array("H")
hts.frombytes(open(r"C:/agentpy/heights.bin", "rb").read())
P = json.load(open(r"C:/agentpy/pond_Swamp_Pond_Water.json"))
SURF = P["surf"]
TUCK = 3.0
LEVEL = SURF + TUCK
BX0, BY0 = P["x0"], P["y0"]
BX1, BY1 = P["x0"] + P["nx"] * P["cell"], P["y0"] + P["ny"] * P["cell"]

z = lambda ix, iy: (hts[iy * W + ix] - MID) * CMU
wx = lambda ix: MINX + ix * SC
wy = lambda iy: MINY + iy * SC
ix0, ix1 = max(0, int((BX0 - MINX) / SC)), min(W - 1, int((BX1 - MINX) / SC))
iy0, iy1 = max(0, int((BY0 - MINY) / SC)), min(H - 1, int((BY1 - MINY) / SC))

# seed: landscape vertices that were under the original water (pond json 'inside') and are below the level
seed = set()
for k, inside in enumerate(P["inside"]):
    if not inside:
        continue
    x, y = P["x0"] + (k % P["nx"]) * P["cell"], P["y0"] + (k // P["nx"]) * P["cell"]
    ix, iy = int(round((x - MINX) / SC)), int(round((y - MINY) / SC))
    if ix0 <= ix <= ix1 and iy0 <= iy <= iy1 and z(ix, iy) < LEVEL:
        seed.add((ix, iy))
reg = set(seed)
q = deque(seed)
while q:
    ix, iy = q.popleft()
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            a, b = ix + dx, iy + dy
            if (a, b) not in reg and ix0 <= a <= ix1 and iy0 <= b <= iy1 and z(a, b) < LEVEL:
                reg.add((a, b))
                q.append((a, b))

verts, vid, faces = [], {}, []


def V(x, y):
    key = (round(x, 1), round(y, 1))
    if key not in vid:
        vid[key] = len(verts)
        verts.append(key)
    return vid[key]


def val(ix, iy):
    """signed: < 0 = water (in the connected region), >= 0 = dry"""
    return z(ix, iy) - LEVEL if (ix, iy) in reg else max(0.5, z(ix, iy) - LEVEL)


cells = {(ix, iy) for (x0, y0) in reg for (ix, iy) in ((x0 - 1, y0 - 1), (x0 - 1, y0), (x0, y0 - 1), (x0, y0))}
for (ix, iy) in cells:
    if not (ix0 <= ix < ix1 and iy0 <= iy < iy1):
        continue
    corners = [(ix, iy), (ix + 1, iy), (ix + 1, iy + 1), (ix, iy + 1)]       # counter-clockwise
    vals = [val(a, b) for a, b in corners]
    if all(v >= 0 for v in vals):
        continue
    poly = []
    for k in range(4):
        (a0, b0), (a1, b1) = corners[k], corners[(k + 1) % 4]
        v0, v1 = vals[k], vals[(k + 1) % 4]
        if v0 < 0:
            poly.append((wx(a0), wy(b0)))
        if (v0 < 0) != (v1 < 0):
            t = v0 / (v0 - v1)
            poly.append((wx(a0) + (wx(a1) - wx(a0)) * t, wy(b0) + (wy(b1) - wy(b0)) * t))
    if len(poly) < 3:
        continue
    ids = [V(x, y) for x, y in poly]
    if len(ids) == 6 and sum(1 for v in vals if v < 0) == 2:               # saddle: two separate corner triangles
        faces.append((ids[0], ids[1], ids[5]))
        faces.append((ids[2], ids[3], ids[4]))
        continue
    for k in range(1, len(ids) - 1):
        faces.append((ids[0], ids[k], ids[k + 1]))

xs = [v[0] for v in verts]
ys = [v[1] for v in verts]
cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
json.dump({"centre": [cx, cy, SURF], "verts": [[x - cx, y - cy] for x, y in verts], "faces": faces},
          open(r"C:/agentpy/swamp_water_smooth.json", "w"))
print("region vertices %d, verts %d, tris %d, centre (%.1f, %.1f, %.1f), box x %.0f..%.0f y %.0f..%.0f" % (
    len(reg), len(verts), len(faces), cx, cy, SURF, min(xs), max(xs), min(ys), max(ys)))
