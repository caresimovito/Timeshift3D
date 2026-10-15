import bpy, mathutils
from mathutils import Vector as V
from mathutils.kdtree import KDTree
BLEND = r"C:\repos\Unreal Projects\Timeshift3D\SourceArt\Enemies\rex4_tripo\rex4_rig.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND)
mesh = bpy.data.objects["SK_Rex4"]; vg = mesh.vertex_groups
names = {g.index: g.name for g in vg}
def side(nm):
    return 'l' if nm.endswith('_l') else ('r' if nm.endswith('_r') else None)
removed = 0
LIP0, LIP1 = V((4.85, 0, 5.25)), V((6.30, 0, 4.75))
def lip_z(x):
    t = max(0.0, min(1.0, (x - LIP0.x) / (LIP1.x - LIP0.x)))
    return LIP0.z + t * (LIP1.z - LIP0.z)
jaw_g = vg["jaw"]; head_g = vg["head"]
for v in mesh.data.vertices:
    for g in list(v.groups):
        nm = names[g.group]; s = side(nm)
        if (s == 'l' and v.co.y < -0.02) or (s == 'r' and v.co.y > 0.02):
            vg[g.group].remove([v.index]); removed += 1
    # jaw only on lower-jaw verts
    is_lower = v.co.x > 4.85 and v.co.z < lip_z(v.co.x)
    for g in list(v.groups):
        if names[g.group] == 'jaw' and not is_lower:
            w = g.weight; jaw_g.remove([v.index]); head_g.add([v.index], w, 'ADD'); removed += 1
    if is_lower and v.co.x > 5.05:
        for g in list(v.groups):
            if names[g.group] in ('head', 'neck_02'):
                w = g.weight; vg[g.group].remove([v.index]); jaw_g.add([v.index], w, 'ADD')
print("[CW] removed/moved", removed)
# fill unweighted from nearest weighted vertex
weighted = [v for v in mesh.data.vertices if v.groups]
kd = KDTree(len(weighted))
for i, v in enumerate(weighted): kd.insert(v.co, i)
kd.balance()
filled = 0
for v in mesh.data.vertices:
    if not v.groups:
        co, i, d = kd.find(v.co)
        for g in weighted[i].groups:
            vg[g.group].add([v.index], g.weight, 'REPLACE')
        filled += 1
print("[CW] filled", filled)
# normalize
bpy.context.view_layer.objects.active = mesh
mesh.select_set(True)
bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
bpy.ops.object.vertex_group_normalize_all(lock_active=False)
bpy.ops.object.mode_set(mode='OBJECT')
cnt = {}
for v in mesh.data.vertices:
    for g in v.groups:
        if g.weight > 0.05: cnt[names[g.group]] = cnt.get(names[g.group], 0) + 1
print("[CW] verts per bone:", sorted(cnt.items(), key=lambda kv: -kv[1]))
both = sum(1 for v in mesh.data.vertices if {side(names[g.group]) for g in v.groups if g.weight > 0.01} >= {'l', 'r'})
print("[CW] verts with both-side limb weights:", both, " unweighted:", sum(1 for v in mesh.data.vertices if not v.groups))
bpy.ops.wm.save_as_mainfile(filepath=BLEND)
print("[CW] saved")
