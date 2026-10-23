# Blender headless: the Tripo key ring (stone ring with cyan runes and two blue crystals) -> the 3 KEY PIECES: decimated, cut
# into three 120-degree arcs (cuts at 0 / 120 / 240 deg around the ring's own axis, so neither crystal at 90 / 270 is cut),
# cut faces filled, each arc ~50 cm long with its origin at its bottom centre; GLB per arc + a preview of all three.
import math
import sys
import bpy
from mathutils import Vector, Matrix
args = sys.argv[sys.argv.index("--") + 1:]
src, outdir, png = args[:3]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
for o in bpy.context.scene.objects:
    o.select_set(o in meshes)
bpy.context.view_layer.objects.active = meshes[0]
if len(meshes) > 1:
    bpy.ops.object.join()
ring = bpy.context.view_layer.objects.active
bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
for o in list(bpy.context.scene.objects):
    if o != ring:
        bpy.data.objects.remove(o)
n0 = len(ring.data.polygons)
m = ring.modifiers.new("dec", "DECIMATE")
m.ratio = min(1.0, 36000.0 / n0)
bpy.ops.object.modifier_apply(modifier="dec")
vs = [v.co.copy() for v in ring.data.vertices]
mn = Vector((min(v.x for v in vs), min(v.y for v in vs), min(v.z for v in vs)))
mx = Vector((max(v.x for v in vs), max(v.y for v in vs), max(v.z for v in vs)))
c = (mn + mx) / 2
ext = mx - mn
axis = min(range(3), key=lambda i: ext[i])            # thinnest = the ring's normal
u, w = [i for i in range(3) if i != axis]             # the ring's plane
print("[RING] faces %d -> %d, extent %s, normal axis %d" % (n0, len(ring.data.polygons), tuple(round(e, 3) for e in ext), axis))


def unit(i, a, b):
    v = [0.0, 0.0, 0.0]
    v[u], v[w] = a, b
    return Vector(v)


for k in range(3):
    a0, a1 = math.radians(120 * k), math.radians(120 * k + 120)
    bpy.ops.object.select_all(action="DESELECT")
    ring.select_set(True)
    bpy.context.view_layer.objects.active = ring
    bpy.ops.object.duplicate()
    pc = bpy.context.view_layer.objects.active
    pc.name = "SM_KeyPiece_%d" % (k + 1)
    bpy.ops.object.mode_set(mode="EDIT")
    for ang, keep_ccw in ((a0, True), (a1, False)):
        # plane through the centre containing the ring axis; its normal points towards the kept side
        d = unit(0, math.cos(ang), math.sin(ang))
        nrm = unit(0, -math.sin(ang), math.cos(ang)) * (1 if keep_ccw else -1)
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.bisect(plane_co=c, plane_no=nrm, clear_inner=True, clear_outer=False, use_fill=True)
    bpy.ops.object.mode_set(mode="OBJECT")
    pv = [pc.matrix_world @ v.co for v in pc.data.vertices]
    if not pv:
        print("[RING] piece %d empty" % (k + 1))
        continue
    s = 0.5 / max(max(p[i] for p in pv) - min(p[i] for p in pv) for i in range(3))
    pc.data.transform(Matrix.Scale(s, 4))
    pv = [v.co for v in pc.data.vertices]
    bc = Vector(((min(p.x for p in pv) + max(p.x for p in pv)) / 2, (min(p.y for p in pv) + max(p.y for p in pv)) / 2, min(p.z for p in pv)))
    pc.data.transform(Matrix.Translation(-bc))
    pc.location = (0, 0, 0)
    bpy.ops.object.select_all(action="DESELECT")
    pc.select_set(True)
    bpy.ops.export_scene.gltf(filepath="%s/SM_KeyPiece_%d.glb" % (outdir, k + 1), export_format="GLB", use_selection=True)
    pc.location = ((k - 1) * 0.65, 0, 0)
    print("[RING] piece %d faces %d size %s" % (k + 1, len(pc.data.polygons), tuple(round(d, 2) for d in pc.dimensions)))
bpy.data.objects.remove(ring)
for img in bpy.data.images:
    pass
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
bpy.context.scene.collection.objects.link(cam)
cam.location = (0, -2.0, 0.8)
cam.rotation_euler = (Vector((0, 0, 0.2)) - cam.location).to_track_quat("-Z", "Y").to_euler()
bpy.context.scene.camera = cam
sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
sun.rotation_euler = (0.8, 0.2, 0.6)
bpy.context.scene.collection.objects.link(sun)
wd = bpy.data.worlds.new("w")
wd.color = (0.35, 0.35, 0.38)
bpy.context.scene.world = wd
r = bpy.context.scene.render
try:
    r.engine = "BLENDER_EEVEE_NEXT"
except TypeError:
    r.engine = "BLENDER_EEVEE"
r.resolution_x, r.resolution_y = 900, 420
r.filepath = png
bpy.ops.render.render(write_still=True)
print("[RING] done")
