# Blender headless: build SM_RexCollider = tiny render tri + UCX convex hull fitted to rex4's upper body.
import bpy, bmesh, mathutils
BLEND = r"C:\repos\Unreal Projects\Timeshift3D\SourceArt\Enemies\rex4_tripo\rex4_rig.blend"
OUT = r"C:\repos\Unreal Projects\Timeshift3D\SourceArt\Enemies\rex4_tripo\fbx\SM_RexCollider.fbx"
ZMIN, XTAIL = 2.4, -3.6   # metres: keep the hull above knee height, drop the tail tip
bpy.ops.wm.open_mainfile(filepath=BLEND)
mesh = bpy.data.objects["SK_Rex4"]
V = [mesh.matrix_world @ v.co for v in mesh.data.vertices]
xs = [v.x for v in V]
print("[COL] mesh x %.2f..%.2f z %.2f..%.2f" % (min(xs), max(xs), min(v.z for v in V), max(v.z for v in V)))
pts = []
x0, x1 = max(min(xs), XTAIL), max(xs)
N = 10
for i in range(N + 1):
    a = x0 + (x1 - x0) * i / N
    b = a + (x1 - x0) / N
    sl = [v for v in V if a <= v.x <= b and v.z >= ZMIN]
    if not sl:
        continue
    ymax = max(abs(v.y) for v in sl) * 0.9
    zlo = max(ZMIN, min(v.z for v in sl))
    zhi = max(v.z for v in sl)
    xm = 0.5 * (a + b)
    print("[COL] slice x=%.2f y=+-%.2f z %.2f..%.2f n=%d" % (xm, ymax, zlo, zhi, len(sl)))
    for y in (-ymax, ymax):
        for z in (zlo, zhi):
            pts.append((xm, y, z))
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o)
bm = bmesh.new()
for p in pts:
    bm.verts.new(p)
bmesh.ops.convex_hull(bm, input=bm.verts)
hm = bpy.data.meshes.new("UCX_SM_RexCollider_00")
bm.to_mesh(hm); bm.free()
hull = bpy.data.objects.new("UCX_SM_RexCollider_00", hm)
bpy.context.scene.collection.objects.link(hull)
tm = bpy.data.meshes.new("SM_RexCollider")
tm.from_pydata([(0, 0, 3.0), (0.01, 0, 3.0), (0, 0.01, 3.0)], [], [(0, 1, 2)])
tri = bpy.data.objects.new("SM_RexCollider", tm)
bpy.context.scene.collection.objects.link(tri)
print("[COL] hull verts %d faces %d" % (len(hm.vertices), len(hm.polygons)))
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.fbx(filepath=OUT, use_selection=True, object_types={'MESH'}, apply_scale_options='FBX_SCALE_NONE',
                         global_scale=1.0, mesh_smooth_type='FACE')
print("[COL] written", OUT)
