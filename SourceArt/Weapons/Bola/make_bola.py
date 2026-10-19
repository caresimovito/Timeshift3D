# Blender headless: model a three-stone bola (stones on leather cords tied at a central knot), export FBX + preview.
# Origin = knot, lying flat in XY (it spins about Z in flight). Span ~0.65 m. Geometry scaled x100 before export (cm).
import math
import sys
import bpy
from mathutils import Vector, noise

out_fbx, out_png = sys.argv[sys.argv.index("--") + 1:][:2]
bpy.ops.wm.read_factory_settings(use_empty=True)
scn = bpy.context.scene


def mat(name, rgb, rough):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Roughness"].default_value = rough
    return m


M_STONE = mat("M_BolaStone", (0.33, 0.31, 0.28), 0.85)
M_CORD = mat("M_BolaCord", (0.20, 0.12, 0.06), 0.9)
R = 0.30                                   # cord length knot -> stone
parts = []
for k in range(3):
    a = 2 * math.pi * k / 3 + 0.25
    c = Vector((R * math.cos(a), R * math.sin(a), 0))
    # stone: lumpy icosphere ~7-8 cm
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=0.038, location=c)
    s = bpy.context.active_object
    for v in s.data.vertices:
        n = noise.noise(v.co * 40 + Vector((k * 3.1, 0, 0)))
        v.co *= 1.0 + 0.22 * n
    s.scale = (1.15, 0.95, 0.85)
    s.data.materials.append(M_STONE)
    for p in s.data.polygons:
        p.use_smooth = True
    parts.append(s)
    # cord: a slightly sagging tube from knot to stone (curve with bevel -> mesh)
    cu = bpy.data.curves.new("cord%d" % k, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = 0.0035
    cu.bevel_resolution = 2
    sp = cu.splines.new("BEZIER")
    sp.bezier_points.add(1)
    for i, pt in enumerate((Vector((0, 0, 0)), c * (1 - 0.038 / R))):
        bp = sp.bezier_points[i]
        bp.co = pt
        bp.handle_left_type = bp.handle_right_type = "AUTO"
    sp.bezier_points[1].co.z -= 0.01
    co = bpy.data.objects.new("cord%d" % k, cu)
    scn.collection.objects.link(co)
    co.data.materials.append(M_CORD)
    parts.append(co)
# knot
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.014, location=(0, 0, 0))
kn = bpy.context.active_object
kn.scale = (1.2, 1.2, 0.8)
kn.data.materials.append(M_CORD)
parts.append(kn)

for o in scn.objects:
    o.select_set(True)
bpy.context.view_layer.objects.active = kn
bpy.ops.object.convert(target="MESH")
bpy.ops.object.join()
bola = bpy.context.active_object
bola.name = "SM_Bola"
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=0.02)
bpy.ops.object.mode_set(mode="OBJECT")
d = bola.dimensions
print("[BOLA] dims (m) %.3f x %.3f x %.3f tris=%d" % (d.x, d.y, d.z, sum(len(p.vertices) - 2 for p in bola.data.polygons)))
bola.scale = (100, 100, 100)
bpy.ops.object.transform_apply(scale=True)
bpy.ops.export_scene.fbx(filepath=out_fbx, use_selection=True, apply_unit_scale=True, apply_scale_options="FBX_SCALE_UNITS",
                         axis_forward="X", axis_up="Z", mesh_smooth_type="FACE", add_leaf_bones=False, bake_space_transform=True)
bola.scale = (0.01, 0.01, 0.01)
bpy.ops.object.transform_apply(scale=True)

cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
scn.collection.objects.link(cam)
scn.camera = cam
cam.data.lens = 50
cam.location = (0.55, -0.55, 0.55)
cam.rotation_euler = (Vector((0, 0, 0)) - cam.location).to_track_quat("-Z", "Y").to_euler()
sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
sun.data.energy = 3.0
sun.rotation_euler = (0.7, 0.2, 0.9)
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
scn.render.resolution_x, scn.render.resolution_y = 560, 560
scn.render.filepath = out_png
bpy.ops.render.render(write_still=True)
print("[BOLA] wrote", out_fbx)
