# Editor Python: bone hierarchy of every ground species (one placed enemy each): bone count, names, parents. Writes
# C:/agentpy/skeletons.json and logs a compact comparison (which bone names are common to all).
import json
import unreal
TAG = "[SKS]"
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
FLY = ("Pteranodon", "Tupandactylus", "Dimorphodon", "Pterosaur")
seen = {}
for a in EAS.get_all_level_actors():
    if a.get_class().get_name() != "BP_EnemyBase_C":
        continue
    sp = str(a.get_editor_property("Species"))
    if sp in FLY or sp in seen:
        continue
    seen[sp] = a.get_editor_property("Body")
out = {}
for sp, b in sorted(seen.items()):
    n = b.get_num_bones()
    bones = []
    for i in range(n):
        nm = str(b.get_bone_name(i))
        par = str(b.get_parent_bone(nm))
        bones.append([nm, par])
    out[sp] = bones
json.dump(out, open(r"C:/agentpy/skeletons.json", "w"), indent=0)
common = set.intersection(*[set(x[0] for x in v) for v in out.values()])
unreal.log_warning("%s species=%d common bones (%d): %s" % (TAG, len(out), len(common), sorted(common)))
for sp, v in out.items():
    names = [x[0] for x in v]
    unreal.log_warning("%s %s %d bones; extra vs common: %s" % (TAG, sp, len(v), [x for x in names if x not in common][:20]))
