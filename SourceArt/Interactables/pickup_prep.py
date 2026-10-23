# Blender headless: a Tripo pickup model (millions of tris) -> game prop: joined, decimated to FACES tris, scaled so its
# longest side is SIZE m, origin at the bottom centre (rests on the ground), textures 1K, GLB out + a preview render.
# usage: blender -b -P pickup_prep.py -- in.glb out.glb preview.png NAME SIZE FACES
import math
import sys
import bpy
import bmesh
from mathutils import Vector
args = sys.argv[sys.argv.index("--") + 1:]
src, out, png = args[:3]
NAME = args[3] if len(args) > 3 else "SM_Pickup"
SIZE = float(args[4]) if len(args) > 4 else 0.45
FACES = float(args[5]) if len(args) > 5 else 8000.0
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
for o in bpy.context.scene.objects:
    o.select_set(False)
for o in meshes:
    o.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
if len(meshes) > 1:
    bpy.ops.object.join()
ob = bpy.context.view_layer.objects.active
bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
for o in list(bpy.context.scene.objects):
    if o != ob:
        bpy.data.objects.remove(o)
n0 = len(ob.data.polygons)
m = ob.modifiers.new("dec", "DECIMATE")
m.ratio = min(1.0, FACES / max(1, n0))
bpy.ops.object.modifier_apply(modifier="dec")
d = ob.dimensions
s = SIZE / max(d)
ob.scale = (s, s, s)
bpy.ops.object.transform_apply(scale=True)
# origin bottom centre
vs = [ob.matrix_world @ v.co for v in ob.data.vertices]
mn = Vector((min(v.x for v in vs), min(v.y for v in vs), min(v.z for v in vs)))
mx = Vector((max(v.x for v in vs), max(v.y for v in vs), max(v.z for v in vs)))
c = Vector(((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, mn.z))
ob.data.transform(__import__("mathutils").Matrix.Translation(-c))
ob.location = (0, 0, 0)
ob.name = NAME
for img in bpy.data.images:
    if img.size[0] > 1024:
        img.scale(1024, 1024 * img.size[1] // max(1, img.size[0]))
        img.pack()
print("[HERBP] faces %d -> %d, size %.2f x %.2f x %.2f m, images %s" % (n0, len(ob.data.polygons), ob.dimensions.x, ob.dimensions.y, ob.dimensions.z,
      [(i.name, i.size[0]) for i in bpy.data.images]))
bpy.ops.object.select_all(action="SELECT")
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=True)
# preview
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
bpy.context.scene.collection.objects.link(cam)
cam.location = (SIZE * 1.0, -SIZE * 1.2, SIZE * 0.8)
dirv = Vector((0, 0, SIZE * 0.3)) - cam.location
cam.rotation_euler = dirv.to_track_quat("-Z", "Y").to_euler()
bpy.context.scene.camera = cam
sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
sun.rotation_euler = (0.8, 0.2, 0.6)
bpy.context.scene.collection.objects.link(sun)
w = bpy.data.worlds.new("w")
w.color = (0.35, 0.35, 0.38)
bpy.context.scene.world = w
r = bpy.context.scene.render
try:
    r.engine = "BLENDER_EEVEE_NEXT"
except TypeError:
    r.engine = "BLENDER_EEVEE"
r.resolution_x, r.resolution_y = 640, 480
r.filepath = png
bpy.ops.render.render(write_still=True)
print("[HERBP] done")
