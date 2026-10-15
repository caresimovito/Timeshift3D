# Build the Rex3 armature with RexPrime bone names, skin the mesh, clean weights, save.
import bpy, mathutils
from mathutils import Vector as V
BLEND = r"C:\repos\Unreal Projects\Timeshift3D\SourceArt\Enemies\rex4_tripo\rex4_rig.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND)
mesh = bpy.data.objects["SK_Rex4"]
for o in list(bpy.data.objects):
    if o.type == 'ARMATURE': bpy.data.objects.remove(o)
mesh.modifiers.clear(); mesh.vertex_groups.clear(); mesh.parent = None
# joints (x fwd, y left, z up), metres
J = dict(
 pelvis=(0.05, 0, 3.95), sp1=(1.00, 0, 4.15), sp2=(2.00, 0, 4.30), sp3=(2.80, 0, 4.45),
 nk1=(3.35, 0, 4.70), nk2=(3.95, 0, 5.15), head=(4.55, 0, 5.55), snout=(6.15, 0, 5.50),
 jaw0=(4.85, 0, 4.80), jaw1=(6.05, 0, 4.36),
 tl1=(-1.30, 0.0, 4.11), tl2=(-2.60, 0.14, 4.18), tl3=(-3.80, 0.35, 4.27), tl4=(-5.00, 0.55, 4.23), tl5=(-6.20, 0.74, 3.91),
)
LEG = dict(hip=(0.00, 0.90, 3.65), knee=(0.45, 1.05, 2.40), ankle=(0.03, 1.00, 1.25), ball=(0.42, 1.12, 0.24), tip=(1.10, 1.45, 0.10))
ARM = dict(sh=(2.62, 0.72, 3.40), el=(2.56, 0.86, 3.05), wr=(2.76, 0.80, 2.60))
# inside-mesh check for every joint
from mathutils.bvhtree import BVHTree
_bvh = BVHTree.FromObject(mesh, bpy.context.evaluated_depsgraph_get())
def _inside(p):
    p = V(p); n = 0; q = p.copy()
    for _ in range(50):
        hit = _bvh.ray_cast(q, V((0.0123, 0.0071, 1)).normalized())
        if hit[0] is None: break
        n += 1; q = hit[0] + V((0.0123, 0.0071, 1)).normalized() * 1e-4
    return n % 2 == 1
for _k, _p in list(J.items()) + [("L_" + k, p) for k, p in LEG.items()] + [("A_" + k, p) for k, p in ARM.items()]:
    print("[RIG] joint %-8s %s inside=%s" % (_k, _p, _inside(_p)))
arm_obj = bpy.data.objects.new("Rex4_Rig", bpy.data.armatures.new("Rex4_Rig"))
bpy.context.scene.collection.objects.link(arm_obj)
bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode='EDIT')
eb = arm_obj.data.edit_bones
def bone(name, h, t, parent=None, connect=False, deform=True):
    b = eb.new(name); b.head = V(h); b.tail = V(t)
    if parent: b.parent = eb[parent]; b.use_connect = connect
    b.use_deform = deform
    d = (b.tail - b.head).normalized()
    z = V((0, 1, 0)).cross(d)
    if z.length > 1e-4: b.align_roll(z.normalized())
    return b
bone("root", (0, 0, 0), (0.9, 0, 0), deform=False)
bone("pelvis", J['pelvis'], J['sp1'], "root")
bone("spine_01", J['sp1'], J['sp2'], "pelvis", True)
bone("spine_02", J['sp2'], J['sp3'], "spine_01", True)
bone("spine_03", J['sp3'], J['nk1'], "spine_02", True)
bone("neck_01", J['nk1'], J['nk2'], "spine_03", True)
bone("neck_02", J['nk2'], J['head'], "neck_01", True)
bone("head", J['head'], J['snout'], "neck_02", True)
bone("jaw", J['jaw0'], J['jaw1'], "head")
bone("tail_01", J['pelvis'], J['tl1'], "pelvis")
bone("tail_02", J['tl1'], J['tl2'], "tail_01", True)
bone("tail_03", J['tl2'], J['tl3'], "tail_02", True)
bone("tail_04", J['tl3'], J['tl4'], "tail_03", True)
bone("tail_05", J['tl4'], J['tl5'], "tail_04", True)
for s, sy in (("l", 1), ("r", -1)):
    m = lambda p: (p[0], p[1]*sy, p[2])
    bone("thigh_"+s, m(LEG['hip']), m(LEG['knee']), "pelvis")
    bone("calf_"+s, m(LEG['knee']), m(LEG['ankle']), "thigh_"+s, True)
    bone("foot_"+s, m(LEG['ankle']), m(LEG['ball']), "calf_"+s, True)
    bone("toe_"+s, m(LEG['ball']), m(LEG['tip']), "foot_"+s, True)
    bone("upperarm_"+s, m(ARM['sh']), m(ARM['el']), "spine_03")
    bone("lowerarm_"+s, m(ARM['el']), m(ARM['wr']), "upperarm_"+s, True)
bpy.ops.object.mode_set(mode='OBJECT')
# skin
for o in bpy.context.selected_objects: o.select_set(False)
mesh.select_set(True); arm_obj.select_set(True); bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.parent_set(type='ARMATURE_AUTO')
n = len(mesh.data.vertices)
w = sum(1 for v in mesh.data.vertices if v.groups)
print("[RIG] heat weighted %d / %d" % (w, n))
if w < 0.97 * n:
    print("[RIG] heat failed -> envelope")
    mesh.vertex_groups.clear(); mesh.modifiers.clear(); mesh.parent = None
    for o in bpy.context.selected_objects: o.select_set(False)
    mesh.select_set(True); arm_obj.select_set(True); bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.parent_set(type='ARMATURE_ENVELOPE')
    w = sum(1 for v in mesh.data.vertices if v.groups); print("[RIG] envelope weighted %d / %d" % (w, n))
bpy.ops.wm.save_as_mainfile(filepath=BLEND)
print("[RIG] saved")
