# Editor Python: measure trunks of the tree meshes that need a trunk capsule (from LOD0 vertices): trunk axis = centroid
# of the lowest 6 % of verts; per 10 % height band, the median / 90th percentile distance of verts from that axis. The
# trunk ends where the band radius jumps (branches / crown begin). Writes C:/agentpy/tree_trunks.json.
import json
import math
import unreal
TAG = "[TRK]"
EAL = unreal.EditorAssetLibrary
PATHS = {"SM_FirTree_01": "/Game/Timeshift/Environment/Meshes/FirTree/SM_FirTree_01",
         "SM_IslandTree_01": "/Game/Timeshift/Environment/Meshes/IslandTree/SM_IslandTree_01",
         "SM_TreeFern": "/Game/Timeshift/Environment/Meshes/Jungle/TreeFern/TreeFern/StaticMeshes/SM_TreeFern",
         "SM_BurntTrunk_01": "/Game/Timeshift/Environment/Meshes/AshForest/SM_BurntTrunk_01",
         "SM_BurntTrunk_02": "/Game/Timeshift/Environment/Meshes/AshForest/SM_BurntTrunk_02",
         "SM_BurntTrunk_03": "/Game/Timeshift/Environment/Meshes/AshForest/SM_BurntTrunk_03"}
out = {}
for name, path in PATHS.items():
    m = EAL.load_asset(path)
    b = m.get_bounding_box()
    h = b.max.z - b.min.z
    pts = []
    for s in range(m.get_num_sections(0)):
        v, *_ = unreal.ProceduralMeshLibrary.get_section_from_static_mesh(m, 0, s)
        pts += v
    low = [p for p in pts if p.z < b.min.z + 0.06 * h]
    cx = sum(p.x for p in low) / max(1, len(low))
    cy = sum(p.y for p in low) / max(1, len(low))
    bands = []
    for k in range(10):
        f0 = k / 10.0
        band = sorted(math.hypot(p.x - cx, p.y - cy) for p in pts if b.min.z + f0 * h <= p.z < b.min.z + (f0 + 0.1) * h)
        bands.append((f0, len(band), band[len(band) // 2] if band else -1, band[int(len(band) * 0.9)] if band else -1))
    out[name] = {"path": path, "zmin": b.min.z, "h": h, "axis": [cx, cy], "bands": bands}
    unreal.log_warning("%s %-17s verts=%d h=%.0f zmin=%.0f axis=(%.0f,%.0f) | %s" % (TAG, name, len(pts), h, b.min.z, cx, cy,
                       " ".join("%d%%:r50=%d r90=%d" % (f0 * 100, r50, r90) for f0, n, r50, r90 in bands)))
json.dump(out, open(r"C:/agentpy/tree_trunks.json", "w"), indent=1)
unreal.log_warning("%s done" % TAG)
