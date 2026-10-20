# Editor Python: why do Psittacosaurus / Archaeoceratops / Caudipteryx clips collapse? Compare each bone's local transform
# in the Idle clip (frame 0) with the skeleton's reference pose (read from a temporary EMPTY AnimSequence: bones without
# tracks evaluate to the ref pose).
import json
import unreal
TAG = "[BAD]"
EAL = unreal.EditorAssetLibrary
SKEL = json.load(open(r"C:/agentpy/skeletons.json"))
TMP = "/Game/Timeshift/Temp"


def ref_seq(sp):
    skel = EAL.load_asset("/Game/Timeshift/Enemies/%s/SK_%s" % (sp, sp)).skeleton
    name = "TMP_RefPose_%s" % sp
    if EAL.does_asset_exist(TMP + "/" + name):
        return EAL.load_asset(TMP + "/" + name)
    f = unreal.AnimSequenceFactory()
    f.set_editor_property("target_skeleton", skel)
    seq = unreal.AssetToolsHelpers.get_asset_tools().create_asset(name, TMP, unreal.AnimSequence, f)
    c = seq.get_editor_property("controller")
    c.open_bracket(unreal.Text("ref"), True)
    c.set_frame_rate(unreal.FrameRate(30, 1), True)
    c.set_number_of_frames(unreal.FrameNumber(1), True)
    c.close_bracket(True)
    return seq


for sp in globals().get("SPS", ["Psittacosaurus", "Archaeoceratops", "Caudipteryx", "Raptor"]):
    n = "SK_%s_Anim_SK_%s_Idle" % (sp, sp)
    idle = EAL.load_asset("/Game/Timeshift/Enemies/%s/%s" % (sp, n))
    ref = ref_seq(sp)
    tracks = list(unreal.AnimationLibrary.get_animation_track_names(idle)) if hasattr(unreal.AnimationLibrary, "get_animation_track_names") else []
    rows = []
    for nm, par in SKEL[sp][:12]:
        a = unreal.AnimationLibrary.get_bone_pose_for_frame(idle, nm, 0, False)
        r = unreal.AnimationLibrary.get_bone_pose_for_frame(ref, nm, 0, False)
        rows.append("%s: idle t=(%.1f,%.1f,%.1f) s=%.2f | ref t=(%.1f,%.1f,%.1f) s=%.2f" % (nm, a.translation.x, a.translation.y, a.translation.z, a.scale3d.x,
                    r.translation.x, r.translation.y, r.translation.z, r.scale3d.x))
    unreal.log_warning("%s %s tracks=%d frames=%s retargetSrc=%s" % (TAG, sp, len(tracks), idle.get_editor_property("number_of_sampled_frames") if True else "?",
                       idle.get_editor_property("retarget_source") if True else "?"))
    for r_ in rows:
        unreal.log_warning("%s   %s" % (TAG, r_))
