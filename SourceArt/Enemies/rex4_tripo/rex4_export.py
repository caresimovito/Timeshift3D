# Export rex4: mesh+rig in rest pose (SK_Rex4_mesh.fbx) and one FBX per action, FBX_SCALE_NONE (UE does m->cm).
import bpy, os
SRC = r"C:\repos\Unreal Projects\Timeshift3D\SourceArt\Enemies\rex4_tripo\rex4_rig.blend"
OUT = r"C:\repos\Unreal Projects\Timeshift3D\SourceArt\Enemies\rex4_tripo\fbx"
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=SRC)
rig = bpy.data.objects["Rex4_Rig"]; mesh = bpy.data.objects["SK_Rex4"]
sc = bpy.context.scene; sc.render.fps = 30
for o in list(bpy.data.objects):
    if o not in (rig, mesh):
        bpy.data.objects.remove(o)
common = dict(use_selection=True, object_types={'ARMATURE', 'MESH'}, add_leaf_bones=False,
              apply_scale_options='FBX_SCALE_NONE', global_scale=1.0, mesh_smooth_type='FACE', path_mode='COPY',
              embed_textures=False, use_armature_deform_only=False, primary_bone_axis='Y', secondary_bone_axis='X')


def select():
    bpy.ops.object.select_all(action='DESELECT')
    rig.select_set(True); mesh.select_set(True); bpy.context.view_layer.objects.active = rig


# rest-pose mesh
rig.animation_data.action = None
for pb in rig.pose.bones:
    pb.rotation_mode = 'XYZ'; pb.rotation_euler = (0, 0, 0); pb.location = (0, 0, 0)
select()
bpy.ops.export_scene.fbx(filepath=os.path.join(OUT, "SK_Rex4_mesh.fbx"), bake_anim=False, **common)
print("[EXP] mesh written", flush=True)
for name in sorted(a.name for a in bpy.data.actions if a.name.startswith("Rex4_")):
    act = bpy.data.actions[name]
    rig.animation_data.action = act
    f0, f1 = int(act.frame_range[0]), int(act.frame_range[1])
    sc.frame_start, sc.frame_end = f0, f1
    select()
    bpy.ops.export_scene.fbx(filepath=os.path.join(OUT, name + ".fbx"), bake_anim=True, bake_anim_use_all_bones=True,
                             bake_anim_use_nla_strips=False, bake_anim_use_all_actions=False,
                             bake_anim_force_startend_keying=True, bake_anim_step=1.0, bake_anim_simplify_factor=0.0, **common)
    print("[EXP] %-12s frames %d..%d" % (name, f0, f1), flush=True)
print("[EXP] DONE", flush=True)
