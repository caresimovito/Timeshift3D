# Unreal editor Python: import single rex footsteps and put PlaySound notifies on foot contacts of walk/run clips.
import os
import unreal

TAG = "[R4F]"
SRC = r"C:\repos\Unreal Projects\Timeshift3D\SourceArt\Audio\Rex"
SND = "/Game/Timeshift/Audio/SFX/Creatures"
ANIM = "/Game/Timeshift/Enemies/RexPrime/SK_RexPrime_Anim_SK_RexPrime_"
EAL = unreal.EditorAssetLibrary
AL = unreal.AnimationLibrary


def log(m):
    unreal.log_warning("%s %s" % (TAG, m))


ref = EAL.load_asset(SND + "/S_RexPrime_Walk_01")
att = EAL.load_asset("/Game/Timeshift/Audio/Attenuation/SA_Creature_Large")
cls = ref.get_editor_property("sound_class_object") if ref else None
steps = []
for i in range(1, 5):
    name = "S_RexPrime_Step_0%d" % i
    t = unreal.AssetImportTask()
    t.set_editor_property("filename", os.path.join(SRC, name + ".wav"))
    t.set_editor_property("destination_path", SND)
    t.set_editor_property("destination_name", name)
    t.set_editor_property("replace_existing", True)
    t.set_editor_property("automated", True)
    t.set_editor_property("save", False)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
    s = EAL.load_asset("%s/%s" % (SND, name))
    if att:
        s.set_editor_property("attenuation_settings", att)
    if cls:
        s.set_editor_property("sound_class_object", cls)
    EAL.save_asset(s.get_path_name(), only_if_is_dirty=False)
    steps.append(s)
    log("sound %s %.2fs attenuation=%s" % (name, s.get_editor_property("duration"), att.get_name() if att else None))

# clip -> [(time, foot, step index, pitch)]
WALK = [(0.02, "toe_l", 0, 0.95), (1.02, "toe_r", 1, 1.0)]
RUN = [(0.02, "toe_l", 2, 1.05), (0.57, "toe_r", 3, 1.1)]
PLAN = {"Walk": WALK, "Walk_Wounded": WALK, "Turn_L": WALK, "Turn_R": WALK, "Run": RUN, "Attack_Charge": RUN}
for clip, events in PLAN.items():
    a = EAL.load_asset(ANIM + clip)
    if a is None:
        log("missing %s" % clip); continue
    AL.remove_animation_notify_events_by_track(a, "Footsteps") if "Footsteps" in [str(n) for n in AL.get_animation_notify_track_names(a)] else None
    if "Footsteps" not in [str(n) for n in AL.get_animation_notify_track_names(a)]:
        AL.add_animation_notify_track(a, "Footsteps")
    for tm, foot, si, pitch in events:
        n = AL.add_animation_notify_event(a, "Footsteps", tm, unreal.AnimNotify_PlaySound)
        n.set_editor_property("sound", steps[si])
        n.set_editor_property("volume_multiplier", 1.0)
        n.set_editor_property("pitch_multiplier", pitch)
        n.set_editor_property("follow", True)
        n.set_editor_property("attach_name", foot)
    EAL.save_asset(a.get_path_name(), only_if_is_dirty=False)
    evs = AL.get_animation_notify_events(a)
    log("%-14s %.2fs notifies %s" % (clip, a.get_play_length(), [round(AL.get_anim_notify_event_trigger_time(e), 2) for e in evs]))
log("DONE")
