# Blender headless: model a small leather belt pouch and export FBX + preview renders.
# Pouch axes: origin at the centre of the opening (top), +X = front (faces away from the body), +Z = up, -X = belt side.
# Size (m): ~0.12 wide (Y), ~0.06 deep (X), ~0.13 tall. Exported in centimetres for Unreal.
import math
import sys
import bmesh
import bpy
from mathutils import Vector, noise

out_fbx, out_png = sys.argv[sys.argv.index("--") + 1:][:2]
bpy.ops.wm.read_factory_settings(use_empty=True)
scn = bpy.context.scene
W, D, H = 0.115, 0.055, 0.125          # body width (Y), depth (X), height (Z)


def mat(name, rgb, rough):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Roughness"].default_value = rough
    return m


M_BODY = mat("M_PouchLeather", (0.16, 0.085, 0.04), 0.75)
M_CORD = mat("M_PouchCord", (0.09, 0.06, 0.035), 0.9)

# --- body: parametric sack. Cross-section = superellipse (rounded rectangle), flat back, bulging front,
#     closed with a rounded bottom and a slightly gathered mouth at z=0.
AF, AB = 0.030, 0.013                  # front / back half-depth
rings, around = 26, 40
verts, faces = [], []
for i in range(rings + 1):
    t = i / rings                                       # 0 mouth .. 1 bottom
    z = -t * H
    shrink = 1.0 if t < 0.72 else math.sqrt(max(0.0, 1 - ((t - 0.72) / 0.28) ** 2))   # round the bottom
    mouth = 1.0 - 0.10 * max(0.0, 0.2 - t) / 0.2                                        # gather the mouth
    for j in range(around):
        th = 2 * math.pi * j / around
        c, sn = math.cos(th), math.sin(th)
        ex = math.copysign(abs(c) ** 0.5, c)            # superellipse exponent 4
        ey = math.copysign(abs(sn) ** 0.5, sn)
        a = AF * (1 + 0.25 * math.sin(math.pi * min(1.0, t * 1.2))) if c > 0 else AB
        x, y = a * ex * shrink * mouth, (W / 2) * ey * shrink * mouth
        n = noise.noise(Vector((x, y, z)) * 55)
        verts.append((x + 0.0015 * n * (1 if c > 0 else 0.3), y + 0.0008 * n, z))
for i in range(rings):
    for j in range(around):
        a, b = i * around + j, i * around + (j + 1) % around
        faces.append((a, b, b + around, a + around))
verts.append((0, 0, -H))                                # bottom pole
bot = len(verts) - 1
last = rings * around
for j in range(around):
    faces.append((last + j, last + (j + 1) % around, bot))
verts.append((0, 0, 0.002))                             # mouth cap (hidden under the flap)
top = len(verts) - 1
for j in range(around):
    faces.append(((j + 1) % around, j, top))
me = bpy.data.meshes.new("body")
me.from_pydata(verts, [], faces)
me.validate()
body = bpy.data.objects.new("PouchBody", me)
scn.collection.objects.link(body)
bpy.context.view_layer.objects.active = body
body.data.materials.append(M_BODY)
for p in body.data.polygons:
    p.use_smooth = True

# --- flap: a strip that leaves the back top edge, arcs over the mouth and hangs down the front
CX, RX = (AF - AB) / 2, (AF + AB) / 2 + 0.005
segs, cols = 28, 14
verts, faces = [], []
for i in range(segs + 1):
    u = i / segs
    if u < 0.45:                                       # arc over the top
        a = math.pi * (1 - u / 0.45)
        px, pz = CX + RX * math.cos(a), 0.004 + 0.018 * math.sin(a)
    else:                                              # hang down the front
        k = (u - 0.45) / 0.55
        px, pz = CX + RX + 0.008 * math.sin(k * math.pi * 0.9), -k * 0.07
    for j in range(cols + 1):
        s = j / cols - 0.5
        half = W * 0.53
        if u > 0.8:                                    # round the bottom corners of the flap
            half *= math.sqrt(max(0.0, 1 - ((u - 0.8) / 0.2) ** 2 * 0.55))
        verts.append((px, s * 2 * half, pz))
for i in range(segs):
    for j in range(cols):
        a = i * (cols + 1) + j
        faces.append((a, a + 1, a + cols + 2, a + cols + 1))
me = bpy.data.meshes.new("flap")
me.from_pydata(verts, [], faces)
flap = bpy.data.objects.new("PouchFlap", me)
scn.collection.objects.link(flap)
sol = flap.modifiers.new("solid", "SOLIDIFY")
sol.thickness = 0.0035
flap.data.materials.append(M_BODY)
for p in flap.data.polygons:
    p.use_smooth = True

# --- toggle (bone/wood peg) + its loop on the flap front
bpy.ops.mesh.primitive_cylinder_add(radius=0.0045, depth=0.028, location=(CX + RX + 0.016, 0, -0.06), rotation=(math.pi / 2, 0, 0))
tog = bpy.context.active_object
tog.data.materials.append(M_CORD)
bpy.ops.mesh.primitive_torus_add(major_radius=0.008, minor_radius=0.0016, location=(CX + RX + 0.011, 0, -0.054),
                                 rotation=(0, math.pi / 2, 0))
tl = bpy.context.active_object
tl.data.materials.append(M_CORD)

# --- belt loop on the back
bpy.ops.mesh.primitive_cube_add(size=1, location=(-AB - 0.004, 0, -0.035))
loop = bpy.context.active_object
loop.scale = (0.005, 0.04, 0.06)
loop.data.materials.append(M_BODY)
bev = loop.modifiers.new("bev", "BEVEL")
bev.width = 0.0015
bev.segments = 2

for o in scn.objects:
    o.select_set(True)
bpy.context.view_layer.objects.active = body
bpy.ops.object.convert(target="MESH")
bpy.ops.object.join()
pouch = bpy.context.active_object
pouch.name = "SM_Pouch"
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.normals_make_consistent(inside=False)   # body faces were wound inward -> looked hollow in game
bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=0.02)
bpy.ops.object.mode_set(mode="OBJECT")
dims = pouch.dimensions
print("[POUCH] dims (m) x=%.3f y=%.3f z=%.3f tris=%d" % (dims.x, dims.y, dims.z, sum(len(p.vertices) - 2 for p in pouch.data.polygons)))
pouch.scale = (100, 100, 100)   # Unreal reads these units as cm
bpy.ops.object.transform_apply(scale=True)
bpy.ops.export_scene.fbx(filepath=out_fbx, use_selection=True, apply_unit_scale=True, apply_scale_options="FBX_SCALE_UNITS",
                         axis_forward="X", axis_up="Z", mesh_smooth_type="FACE", add_leaf_bones=False, bake_space_transform=True)

pouch.scale = (0.01, 0.01, 0.01)
bpy.ops.object.transform_apply(scale=True)
# previews: front three-quarter and side
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
scn.collection.objects.link(cam)
scn.camera = cam
cam.data.lens = 60
sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
sun.data.energy = 3.0
sun.rotation_euler = (0.8, 0.2, 0.9)
scn.collection.objects.link(sun)
scn.world = bpy.data.worlds.new("w")
scn.world.use_nodes = True
scn.world.node_tree.nodes["Background"].inputs[0].default_value = (0.5, 0.52, 0.55, 1)
for eng in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
    try:
        scn.render.engine = eng
        break
    except TypeError:
        pass
scn.render.resolution_x, scn.render.resolution_y = 480, 480
for tag, loc in (("a", (0.30, 0.20, 0.03)), ("b", (0.0, 0.34, -0.05))):
    cam.location = loc
    cam.rotation_euler = (Vector((0, 0, -0.06)) - cam.location).to_track_quat("-Z", "Y").to_euler()
    scn.render.filepath = out_png.replace(".png", "_%s.png" % tag)
    bpy.ops.render.render(write_still=True)
print("[POUCH] wrote", out_fbx)
# report: fraction of body faces pointing away from the pouch centre (should be ~1.0)
import bmesh as _bm
_b = _bm.new(); _b.from_mesh(pouch.data)
c = Vector((0, 0, -0.06))
front = [f for f in _b.faces if f.calc_center_median().x > 0.025 and -0.12 < f.calc_center_median().z < -0.08]
bottom = [f for f in _b.faces if f.calc_center_median().z < -0.135]
print("[POUCH] lower-front faces facing +X: %d / %d ; bottom faces facing down: %d / %d" % (
    sum(1 for f in front if f.normal.x > 0), len(front), sum(1 for f in bottom if f.normal.z < 0), len(bottom)))
