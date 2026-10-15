# Fresh process: evaluate the deformed mesh per frame of one action and shift the root so the lowest skin point
# sits on z=0 once the body is falling/lying (frames after t0). Writes root location curves, saves.
import bpy, sys
from mathutils import Vector as V
BLEND = r"C:\repos\Unreal Projects\Timeshift3D\SourceArt\Enemies\rex4_tripo\rex4_rig.blend"
act_name, t0 = sys.argv[sys.argv.index("--") + 1], float(sys.argv[sys.argv.index("--") + 2])
bpy.ops.wm.open_mainfile(filepath=BLEND)
arm = bpy.data.objects["Rex4_Rig"]; mesh = bpy.data.objects["SK_Rex4"]
act = bpy.data.actions[act_name]; arm.animation_data.action = act
sc = bpy.context.scene; f0, f1 = int(act.frame_range[0]), int(act.frame_range[1])
step = 7
idx = list(range(0, len(mesh.data.vertices), step))
mins = {}
for f in range(f0, f1 + 1):
    sc.frame_set(f)
    dg = bpy.context.evaluated_depsgraph_get(); ev = mesh.evaluated_get(dg); me = ev.to_mesh()
    mw = ev.matrix_world
    mins[f] = min((mw @ me.vertices[i].co).z for i in idx)
    ev.to_mesh_clear()
print("[GROUND] before: " + " ".join("%d:%.2f" % (f, mins[f]) for f in range(f0, f1 + 1, 6)))
R3 = arm.data.bones["root"].matrix_local.to_3x3().inverted()
from bpy_extras import anim_utils
cb = anim_utils.action_get_channelbag_for_slot(act, act.slots[0])
curves = {i: cb.fcurves.find('pose.bones["root"].location', index=i) for i in range(3)}
for i in range(3):
    if curves[i] is None:
        curves[i] = act.fcurve_ensure_for_datablock(arm, 'pose.bones["root"].location', index=i)
fs0 = int(round(t0 * sc.render.fps))
for f in range(f0, f1 + 1):
    if f < fs0:
        continue
    w = min(1.0, (f - fs0) / 6.0)
    dz = -mins[f] * w
    cur = V([curves[i].evaluate(f) for i in range(3)])
    new = cur + R3 @ V((0, 0, dz))
    for i in range(3):
        kps = [k for k in curves[i].keyframe_points if int(round(k.co.x)) == f]
        if kps:
            kps[0].co.y = new[i]
        else:
            curves[i].keyframe_points.insert(f, new[i], options={'FAST'})
for c in curves.values():
    c.update()
bpy.ops.wm.save_as_mainfile(filepath=BLEND)
print("[GROUND] corrected from frame %d, saved" % fs0)
