# Editor Python: measure each cycad mesh's trunk from its vertices (LOD0): for height bands, the radial extent of verts
# near the trunk axis. Lets us replace the whole-crown convex hull with a trunk capsule.
import math
import unreal
TAG = "[TRUNK]"
EAL = unreal.EditorAssetLibrary
for name in ("SM_TreeCycad_01", "SM_TreeCycad_02", "SM_TreeCycad_03"):
    m = EAL.load_asset("/Game/Timeshift/Environment/Meshes/" + name) or [EAL.load_asset(p) for p in EAL.list_assets("/Game/Timeshift", True) if p.split(".")[-1] == name][0]
    b = m.get_bounding_box()
    h = b.max.z - b.min.z
    pts = []
    for s in range(m.get_num_sections(0)):
        v, *_ = unreal.ProceduralMeshLibrary.get_section_from_static_mesh(m, 0, s)
        pts += v
    # trunk axis = centroid of the lowest 8% of verts
    low = [p for p in pts if p.z < b.min.z + 0.08 * h]
    cx = sum(p.x for p in low) / max(1, len(low))
    cy = sum(p.y for p in low) / max(1, len(low))
    bands = []
    for f0 in (0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7):
        band = [math.hypot(p.x - cx, p.y - cy) for p in pts if b.min.z + f0 * h <= p.z < b.min.z + (f0 + 0.1) * h]
        band.sort()
        bands.append("%d%%:n%d r50=%d r90=%d" % (f0 * 100, len(band), band[len(band) // 2] if band else -1, band[int(len(band) * 0.9)] if band else -1))
    unreal.log_warning("%s %s path=%s verts=%d h=%.0f zmin=%.0f axis=(%.0f,%.0f) | %s" % (TAG, name, m.get_path_name(), len(pts), h, b.min.z, cx, cy, " ".join(bands)))
