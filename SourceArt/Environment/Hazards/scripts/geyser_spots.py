# Offline: pick 3 geyser spots inside the real swamp water (same flood fill as build_pond_mesh.py, no dilation),
# 25-60 cm deep, >= 3 cells from the shore, clear of the tar/mud zones, spread apart. -> geyser_spots.json
import json
from collections import deque

d = json.load(open(r"C:/agentpy/pond_Swamp_Pond_Water.json"))
nx, ny, c, surf, H, IN = d["nx"], d["ny"], d["cell"], d["surf"], d["h"], d["inside"]
XMIN, YLO, YHI = 23800, -700, 2800
xy = lambda k: (d["x0"] + (k % nx) * c, d["y0"] + (k // nx) * c)
cut = lambda k: xy(k)[0] < XMIN and YLO <= xy(k)[1] <= YHI
wet = [H[k] is not None and H[k] < surf and not cut(k) for k in range(nx * ny)]
reg = [False] * (nx * ny)
q = deque(k for k in range(nx * ny) if wet[k] and IN[k])
for k in q:
    reg[k] = True
while q:
    k = q.popleft()
    i, j = k % nx, k // nx
    for a, b in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
        if 0 <= a < nx and 0 <= b < ny and wet[b * nx + a] and not reg[b * nx + a]:
            reg[b * nx + a] = True
            q.append(b * nx + a)


def interior(k, r=3):
    i, j = k % nx, k // nx
    return all(0 <= i + a < nx and 0 <= j + b < ny and reg[(j + b) * nx + i + a] for a in range(-r, r + 1) for b in range(-r, r + 1))


avoid = [(26100, 100), (37550, 50), (38650, -1250), (24550, -1550)]
cands = []
for k in range(nx * ny):
    if reg[k] and 25 <= surf - H[k] <= 60 and interior(k):
        x, y = xy(k)
        if all(((x - ax) ** 2 + (y - ay) ** 2) ** 0.5 > 1200 for ax, ay in avoid):
            cands.append((x, y, surf - H[k]))
print("water cells", sum(reg), "candidates", len(cands))
cx = sum(x for x, _, _ in cands) / len(cands)
cy = sum(y for _, y, _ in cands) / len(cands)
cands = [p for p in cands if ((p[0] - cx) ** 2 + (p[1] - cy) ** 2) ** 0.5 < 2600]   # keep them where the player goes
print("near centre", len(cands))
picked = [min(cands, key=lambda p: (p[0] - cx) ** 2 + (p[1] - cy) ** 2)]
while len(picked) < 3:
    best = max(cands, key=lambda p: min(((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2) ** 0.5 for q in picked))
    picked.append(best)
for p in picked:
    print("spot (%.0f, %.0f) depth %.0f" % p)
json.dump([[p[0], p[1]] for p in picked], open(r"C:/agentpy/geyser_spots.json", "w"))
