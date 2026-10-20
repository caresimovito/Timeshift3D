# Editor Python: repair the retargeted clips of Psittacosaurus / Archaeoceratops / Caudipteryx.
# Cause (found 2026-10-20): these skeletons come from Blender in metres - the top armature bone (SK_<Species>[1]) carries
# a scale of 100 in the reference pose, which turns every child bone's metre offsets into centimetres. The retargeted clips
# have that bone's scale keyed at 1 (so every bone sits ~100x too close to its parent: the body collapses to a point)
# and the pelvis translation keyed in centimetres instead of metres. Fix: armature-bone scale -> its ref-pose scale,
# pelvis translation / that scale. Everything else is rewritten unchanged. Globals: SPS, CLIPS, DRY.
import json
import unreal
TAG = "[FIX]"
EAL = unreal.EditorAssetLibrary
SKEL = json.load(open(r"C:/agentpy/skeletons.json"))
SPS = globals().get("SPS") or ["Psittacosaurus", "Archaeoceratops", "Caudipteryx"]
CLIPS = globals().get("CLIPS") or ["Idle", "Walk", "Run", "Attack", "Flinch", "Death"]
DRY = globals().get("DRY", False)
AL = unreal.AnimationLibrary


def ref_scale(sp, bone):
    ref = EAL.load_asset("/Game/Timeshift/Temp/TMP_RefPose_%s" % sp)
    return AL.get_bone_pose_for_frame(ref, bone, 0, False).scale3d.x


for sp in SPS:
    bones = [b for b, _ in SKEL[sp]]
    top = bones[0]
    k = ref_scale(sp, top)
    for clip in CLIPS:
        n = "SK_%s_Anim_SK_%s_%s" % (sp, sp, clip)
        path = "/Game/Timeshift/Enemies/%s/%s" % (sp, n)
        if not EAL.does_asset_exist(path):
            unreal.log_warning("%s %s missing" % (TAG, n))
            continue
        seq = EAL.load_asset(path)
        nkeys = AL.get_num_keys(seq) if hasattr(AL, "get_num_keys") else AL.get_num_frames(seq) + 1
        tracks = {}
        for b in bones:
            ps, rs, ss = [], [], []
            for f in range(nkeys):
                tr = AL.get_bone_pose_for_frame(seq, b, f, False)
                p, q, s = tr.translation, tr.rotation, tr.scale3d
                if b == top:
                    s = unreal.Vector(k, k, k)
                elif b == "pelvis" and abs(p.x) + abs(p.y) + abs(p.z) > 3.0:
                    p = unreal.Vector(p.x / k, p.y / k, p.z / k)
                ps.append(unreal.Vector(p.x, p.y, p.z))
                rs.append(unreal.Quat(q.x, q.y, q.z, q.w))
                ss.append(unreal.Vector(s.x, s.y, s.z))
            tracks[b] = (ps, rs, ss)
        top_before = AL.get_bone_pose_for_frame(seq, top, 0, False).scale3d.x
        pel_before = AL.get_bone_pose_for_frame(seq, "pelvis", 0, False).translation
        if not DRY:
            ctrl = seq.get_editor_property("controller")
            ctrl.open_bracket(unreal.Text("fix armature scale"), True)
            for b in bones:
                ctrl.set_bone_track_keys(unreal.Name(b), tracks[b][0], tracks[b][1], tracks[b][2], True)
            ctrl.close_bracket(True)
            EAL.save_asset(seq.get_path_name(), only_if_is_dirty=False)
        after = AL.get_bone_pose_for_frame(seq, "pelvis", 0, False).translation
        unreal.log_warning("%s %s %s keys=%d top scale %.2f -> %.2f | pelvis (%.1f,%.1f,%.1f) -> (%.2f,%.2f,%.2f)%s" % (
            TAG, sp, clip, nkeys, top_before, AL.get_bone_pose_for_frame(seq, top, 0, False).scale3d.x if not DRY else k,
            pel_before.x, pel_before.y, pel_before.z, after.x, after.y, after.z, " (dry)" if DRY else ""))
