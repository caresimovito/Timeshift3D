# Chronoshift - audio skeleton + import
# Run from the Unreal editor console:  py "C:/agentpy/audio_setup.py"
import unreal, os

SRC = r"C:\Users\vitoc\Downloads\chronoshift sounds\converted"
ROOT = "/Game/Timeshift/Audio"
AT = unreal.AssetToolsHelpers.get_asset_tools()
EAL = unreal.EditorAssetLibrary
log = []


def ensure_dir(p):
    if not EAL.does_directory_exist(p):
        EAL.make_directory(p)


def make(name, path, cls, fac):
    full = "%s/%s" % (path, name)
    if EAL.does_asset_exist(full):
        log.append("exists  %s" % full)
        return EAL.load_asset(full)
    a = AT.create_asset(name, path, cls, fac)
    EAL.save_asset(full)
    log.append("created %s" % full)
    return a


for d in ["", "/SFX", "/SFX/Creatures", "/SFX/Player", "/SFX/Weapons",
          "/Ambience", "/Music", "/UI", "/Classes", "/Attenuation", "/Concurrency"]:
    ensure_dir(ROOT + d)

# ---------- 1. Sound class hierarchy ----------
CP = ROOT + "/Classes"
master = make("SC_Master", CP, unreal.SoundClass, unreal.SoundClassFactory())
kids = {}
for n in ["SC_SFX", "SC_Ambience", "SC_Music", "SC_UI"]:
    kids[n] = make(n, CP, unreal.SoundClass, unreal.SoundClassFactory())
try:
    master.set_editor_property("child_classes", list(kids.values()))
    for n, c in kids.items():
        c.set_editor_property("parent_class", master)
    log.append("hierarchy SC_Master -> " + ", ".join(kids.keys()))
except Exception as e:
    log.append("ERR hierarchy: %s" % e)

# ---------- 2. Attenuation ----------
AP = ROOT + "/Attenuation"


def atten(name, falloff, inner):
    a = make(name, AP, unreal.SoundAttenuation, unreal.SoundAttenuationFactory())
    try:
        s = a.get_editor_property("attenuation")
        s.set_editor_property("enable_spatialization", True)
        s.set_editor_property("attenuation_shape_extents", unreal.Vector(inner, 0.0, 0.0))
        s.set_editor_property("falloff_distance", falloff)
        s.set_editor_property("distance_algorithm", unreal.AttenuationDistanceModel.NATURAL_SOUND)
        s.set_editor_property("db_attenuation_at_max", -60.0)
        s.set_editor_property("enable_air_absorption", True)
        a.set_editor_property("attenuation", s)
        log.append("atten %s falloff=%dcm inner=%dcm" % (name, falloff, inner))
    except Exception as e:
        log.append("ERR atten %s: %s" % (name, e))
    return a


sa_large = atten("SA_Creature_Large", 6000.0, 800.0)
sa_small = atten("SA_Creature_Small", 2500.0, 300.0)

# ---------- 3. Concurrency ----------
con = make("SCon_CreatureVocal", ROOT + "/Concurrency",
           unreal.SoundConcurrency, unreal.SoundConcurrencyFactory())
try:
    c = con.get_editor_property("concurrency")
    c.set_editor_property("max_count", 3)
    c.set_editor_property("resolution_rule",
                          unreal.MaxConcurrentResolutionRule.STOP_FARTHEST_THEN_PREVENT_NEW)
    con.set_editor_property("concurrency", c)
    log.append("concurrency max_count=3 stop-farthest-then-prevent-new")
except Exception as e:
    log.append("ERR concurrency: %s" % e)

# ---------- 4. Import the WAVs ----------
LOOPS = set(["S_Creature_Footsteps_Gravel_Loop",
             "S_Pterosaur_Wings_Loop",
             "S_Amb_Jungle_Creatures_Loop",
             "S_Amb_Jungle_Pad_Loop", "S_Amb_Jungle_Dark_Loop",
             "S_Fly_Wings_Loop",
             "S_Foot_Grass_Loop", "S_Foot_Gravel_Loop",
             "S_Foot_Mud_Loop_01", "S_Foot_Mud_Loop_02", "S_Foot_Sand_Loop",
             "S_Wpn_Torch_Burn_Loop_01", "S_Wpn_Torch_Burn_Loop_02"])

# Assets whose source file changed and must be re-imported even though the
# asset already exists. The jungle creatures bed was replaced with a longer,
# higher sample-rate version (143s @ 48kHz, was 59s @ 44.1kHz).
FORCE = set(["S_Amb_Jungle_Creatures_Loop"])


def import_folder(disk_sub, dest):
    d = os.path.join(SRC, disk_sub)
    if not os.path.isdir(d):
        log.append("MISSING source dir %s" % d)
        return []
    tasks = []
    names = []
    skipped = 0
    for f in sorted(os.listdir(d)):
        if not f.lower().endswith(".wav"):
            continue
        base = os.path.splitext(f)[0]
        names.append(base)
        if EAL.does_asset_exist(dest + "/" + base) and base not in FORCE:
            skipped += 1
            continue
        t = unreal.AssetImportTask()
        t.filename = os.path.join(d, f)
        t.destination_path = dest
        t.destination_name = base
        t.automated = True
        t.replace_existing = True
        t.save = True
        tasks.append(t)
    if tasks:
        AT.import_asset_tasks(tasks)
    log.append("imported %d, already present %d -> %s" % (len(tasks), skipped, dest))
    return [dest + "/" + n for n in names]


creature_paths = import_folder("Creatures", ROOT + "/SFX/Creatures")
amb_paths = import_folder("Ambience", ROOT + "/Ambience")
player_paths = import_folder("Player", ROOT + "/SFX/Player")
weapon_paths = import_folder("Weapons", ROOT + "/SFX/Weapons")


# ---------- 5. Assign class / attenuation / looping ----------
def configure(paths, sclass, atten_asset, concurrency):
    n = 0
    for p in paths:
        w = EAL.load_asset(p)
        if not w:
            log.append("  load failed %s" % p)
            continue
        try:
            w.set_editor_property("sound_class_object", sclass)
            if atten_asset:
                w.set_editor_property("attenuation_settings", atten_asset)
            if concurrency:
                w.set_editor_property("sound_concurrency_settings", concurrency)
            if p.rsplit("/", 1)[-1] in LOOPS:
                w.set_editor_property("looping", True)
            EAL.save_asset(p)
            n += 1
        except Exception as e:
            log.append("  ERR %s: %s" % (p, e))
    return n


a = configure(creature_paths, kids["SC_SFX"], sa_large, con)
b = configure(amb_paths, kids["SC_Ambience"], None, None)
c2 = configure(player_paths, kids["SC_SFX"], sa_small, None)
d2 = configure(weapon_paths, kids["SC_SFX"], sa_small, None)
log.append("configured creature=%d ambience=%d player=%d weapon=%d"
           % (a, b, c2, d2))

# NOTE: deliberately no save_directory() here. Calling it with
# only_if_is_dirty=False forces a recursive re-save of every package and goes
# down the checkout/save-prompt path, which hung the editor for over an hour.
# Every asset above is saved individually at the point it is created or edited.
print("\n".join(["[AUDIO] " + l for l in log]))
print("[AUDIO] DONE")
