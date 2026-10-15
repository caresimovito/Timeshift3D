# Import the Tripo rex FBX, orient head to +X, scale to 12.6 m, floor at z=0, centre; save rig blend; render ortho views.
import bpy, bmesh, mathutils, math
SRC = r"C:\repos\Unreal Projects\Timeshift3D\SourceArt\Enemies\rex4_tripo\tripo_convert_adf150cf-38b0-4ae9-bf7e-3c49e711b16c.fbx"
BLEND = r"C:\repos\Unreal Projects\Timeshift3D\SourceArt\Enemies\rex4_tripo\rex4_rig.blend"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=SRC)
o = [x for x in bpy.context.scene.objects if x.type == 'MESH'][0]
for x in list(bpy.context.scene.objects):
    if x != o: bpy.data.objects.remove(x)
o.parent = None
o.data.transform(o.matrix_world); o.matrix_world = mathutils.Matrix.Identity(4)
bm = bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table()
seen = set(); comps = []
for v in bm.verts:
    if v.index in seen: continue
    st = [v]; seen.add(v.index); n = 0
    while st:
        x = st.pop(); n += 1
        for e in x.link_edges:
            y = e.other_vert(x)
            if y.index not in seen: seen.add(y.index); st.append(y)
    comps.append(n)
small = []
seen2 = set()
for v in bm.verts:
    if v.index in seen2: continue
    st = [v]; seen2.add(v.index); grp = []
    while st:
        x = st.pop(); grp.append(x)
        for e in x.link_edges:
            y = e.other_vert(x)
            if y.index not in seen2: seen2.add(y.index); st.append(y)
    if len(grp) < 100: small += grp
bmesh.ops.delete(bm, geom=small, context='VERTS'); bm.to_mesh(o.data)
bm.free()
comps.sort(reverse=True)
print("[PREP] components", len(comps), comps[:6])
V = [v.co for v in o.data.vertices]
# straighten: principal axis of the footprint (XY) -> X
n = len(V); mx = sum(v.x for v in V) / n; my = sum(v.y for v in V) / n
sxx = sum((v.x - mx) ** 2 for v in V) / n; syy = sum((v.y - my) ** 2 for v in V) / n; sxy = sum((v.x - mx) * (v.y - my) for v in V) / n
yaw = 0.5 * math.atan2(2 * sxy, sxx - syy)
print("[PREP] footprint principal axis at %.1f deg" % math.degrees(yaw))
o.data.transform(mathutils.Matrix.Rotation(-yaw, 4, 'Z')); o.data.update()
V = [v.co for v in o.data.vertices]
xs = [v.x for v in V]; ys = [v.y for v in V]
ax = 'x' if (max(xs) - min(xs)) >= (max(ys) - min(ys)) else 'y'
coord = (lambda v: v.x) if ax == 'x' else (lambda v: v.y)
lo = min(coord(v) for v in V); hi = max(coord(v) for v in V); L = hi - lo
def zspan(a, b):
    sel = [v.z for v in V if a <= coord(v) <= b]
    return (max(sel) - min(sel)) if sel else 0
head_hi = zspan(hi - 0.08 * L, hi) > zspan(lo, lo + 0.08 * L)
ang = (0.0 if head_hi else math.pi) if ax == 'x' else (-math.pi / 2 if head_hi else math.pi / 2)
s = 12.6 / L
o.data.transform(mathutils.Matrix.Diagonal((s, s, s, 1.0)) @ mathutils.Matrix.Rotation(ang, 4, 'Z'))
V = [v.co for v in o.data.vertices]
minz = min(v.z for v in V); cx = 0.5 * (min(v.x for v in V) + max(v.x for v in V)); cy = 0.5 * (min(v.y for v in V) + max(v.y for v in V))
for v in o.data.vertices:
    v.co.x -= cx; v.co.y -= cy; v.co.z -= minz
o.data.update()
V = [v.co for v in o.data.vertices]
print("[PREP] axis %s head_hi %s ; bounds x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f" % (ax, head_hi, min(v.x for v in V), max(v.x for v in V), min(v.y for v in V), max(v.y for v in V), min(v.z for v in V), max(v.z for v in V)))
o.name = "SK_Rex4"
bpy.ops.wm.save_as_mainfile(filepath=BLEND, relative_remap=True)
sc = bpy.context.scene
sc.render.engine = 'BLENDER_WORKBENCH'; sc.display.shading.light = 'STUDIO'; sc.display.shading.color_type = 'TEXTURE'
sc.world = bpy.data.worlds.new("w")
cam = bpy.data.objects.new("c", bpy.data.cameras.new("c")); sc.collection.objects.link(cam); sc.camera = cam
cam.data.type = 'ORTHO'
for name, loc, rot, osc, res in (("side", (0, -30, 2.5), (math.radians(90), 0, 0), 14.0, (1400, 700)),
                                 ("front", (30, 0, 2.5), (math.radians(90), 0, math.radians(90)), 7.0, (700, 700))):
    cam.location = loc; cam.rotation_euler = rot; cam.data.ortho_scale = osc
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.filepath = r"C:\agentpy\rex4_%s.png" % name
    bpy.ops.render.render(write_still=True)
print("[PREP] done")
