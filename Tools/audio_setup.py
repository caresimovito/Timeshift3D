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
             "S_Amb_Jungle_Creatures_Loop"])


def import_folder(disk_sub, dest):
    d = os.path.join(SRC, disk_sub)
    if not os.path.isdir(d):
        log.append("MISSING source dir %s" % d)
        return []
    tasks = []
    for f in sorted(os.listdir(d)):
        if not f.lower().endswith(".wav"):
            continue
        t = unreal.AssetImportTask()
        t.filename = os.path.join(d, f)
        t.destination_path = dest
        t.destination_name = os.path.splitext(f)[0]
        t.automated = True
        t.replace_existing = True
        t.save = True
        tasks.append(t)
    if tasks:
        AT.import_asset_tasks(tasks)
    log.append("imported %d wav -> %s" % (len(tasks), dest))
    return [dest + "/" + t.destination_name for t in tasks]


creature_paths = import_folder("Creatures", ROOT + "/SFX/Creatures")
amb_paths = import_folder("Ambience", ROOT + "/Ambience")


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
log.append("configured %d creature + %d ambience waves" % (a, b))

EAL.save_directory(ROOT, only_if_is_dirty=False, recursive=True)
print("\n".join(["[AUDIO] " + l for l in log]))
print("[AUDIO] DONE")
