# Editor Python: geyser assets.
#  - import S_GeyserHiss / S_GeyserBurst (SourceArt/Audio/Hazards) to /Game/Timeshift/Hazards/Audio (attenuated 3D)
#  - NS_GeyserWarn = NS_GeyserWisp duplicate (tuned after via Niagara tools)
#  - M_GeyserCrust: deferred decal, pale sinter crust with orange mineral staining, soft broken edge
#  - BP_GeyserVent: Actor with Trigger capsule (column), Crust decal, Wisp/Warn/Steam Niagara components
import unreal

TAG = "[GEYA]"
EAL = unreal.EditorAssetLibrary
MEL = unreal.MaterialEditingLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
tasks = []
for nm in ("S_GeyserHiss", "S_GeyserBurst"):
    t = unreal.AssetImportTask()
    t.set_editor_property("filename", r"C:/repos/Unreal Projects/Timeshift3D/SourceArt/Audio/Hazards/%s.wav" % nm)
    t.set_editor_property("destination_path", "/Game/Timeshift/Hazards/Audio")
    t.set_editor_property("replace_existing", True)
    t.set_editor_property("automated", True)
    t.set_editor_property("save", True)
    tasks.append(t)
tools.import_asset_tasks(tasks)
att = EAL.load_asset("/Game/Timeshift/Audio/Attenuation/SA_Creature_Large")
sfx = EAL.load_asset("/Game/Timeshift/Audio/Classes/SC_SFX")
for nm in ("S_GeyserHiss", "S_GeyserBurst"):
    s = EAL.load_asset("/Game/Timeshift/Hazards/Audio/" + nm)
    if att:
        s.set_editor_property("attenuation_settings", att)
    if sfx:
        s.set_editor_property("sound_class_object", sfx)
    EAL.save_asset(s.get_path_name(), only_if_is_dirty=False)
if not EAL.does_asset_exist("/Game/Timeshift/Hazards/VFX/NS_GeyserWarn"):
    EAL.duplicate_asset("/Game/Timeshift/Hazards/VFX/NS_GeyserWisp", "/Game/Timeshift/Hazards/VFX/NS_GeyserWarn")
EAL.save_asset("/Game/Timeshift/Hazards/VFX/NS_GeyserWarn", only_if_is_dirty=False)

# ---- crust decal
D = "/Game/Timeshift/Hazards/Materials"
m = EAL.load_asset(D + "/M_GeyserCrust") or tools.create_asset("M_GeyserCrust", D, unreal.Material, unreal.MaterialFactoryNew())
MEL.delete_all_material_expressions(m)
noise = EAL.load_asset("/Game/Timeshift/Environment/Water/Textures/T_Water_Noise")


def node(cls, x, y, **props):
    e = MEL.create_material_expression(m, cls, x, y)
    for k, v in props.items():
        e.set_editor_property(k, v)
    return e


def link(a, b, inp="", out=""):
    if not MEL.connect_material_expressions(a, out, b, inp):
        unreal.log_warning("%s link failed %s.%s -> %s.%s" % (TAG, a.get_name(), out, b.get_name(), inp))


uv = node(unreal.MaterialExpressionTextureCoordinate, -1400, 0)
c = node(unreal.MaterialExpressionConstant2Vector, -1400, 120, r=0.5, g=0.5)
sub = node(unreal.MaterialExpressionSubtract, -1250, 0)
link(uv, sub, "A")
link(c, sub, "B")
ln = node(unreal.MaterialExpressionLength, -1100, 0)
link(sub, ln)
r2 = node(unreal.MaterialExpressionMultiply, -1000, 80, const_b=2.0)
link(ln, r2, "A")
rad = node(unreal.MaterialExpressionOneMinus, -950, 0)
link(r2, rad)
tcn = node(unreal.MaterialExpressionTextureCoordinate, -1400, 300, utiling=3.0, vtiling=3.0)
nz = node(unreal.MaterialExpressionTextureSample, -1200, 300, texture=noise)
link(tcn, nz, "UVs")
nzs = node(unreal.MaterialExpressionMultiply, -950, 300, const_b=0.7)
link(nz, nzs, "A", "R")
edge = node(unreal.MaterialExpressionAdd, -800, 100)
link(rad, edge, "A")
link(nzs, edge, "B")
e3 = node(unreal.MaterialExpressionMultiply, -650, 100, const_b=2.2)
link(edge, e3, "A")
e4 = node(unreal.MaterialExpressionSubtract, -520, 100, const_b=0.85)
link(e3, e4, "A")
op = node(unreal.MaterialExpressionSaturate, -400, 100)
link(e4, op)
# centre: pale grey-white sinter; outer ring: rusty orange iron staining
sinter = node(unreal.MaterialExpressionConstant3Vector, -650, -300, constant=unreal.LinearColor(0.55, 0.52, 0.45, 1))
rust = node(unreal.MaterialExpressionConstant3Vector, -650, -200, constant=unreal.LinearColor(0.42, 0.2, 0.06, 1))
ring = node(unreal.MaterialExpressionSaturate, -650, -100)
rr = node(unreal.MaterialExpressionMultiply, -800, -100, const_b=1.6)
link(rad, rr, "A")
link(rr, ring)
bc0 = node(unreal.MaterialExpressionLinearInterpolate, -450, -250)
link(rust, bc0, "A")
link(sinter, bc0, "B")
link(ring, bc0, "Alpha")
var = node(unreal.MaterialExpressionMultiply, -300, -250)
link(bc0, var, "A")
vn = node(unreal.MaterialExpressionLinearInterpolate, -450, -120, const_a=0.75, const_b=1.1)
link(nz, vn, "Alpha", "G")
link(vn, var, "B")
rough = node(unreal.MaterialExpressionLinearInterpolate, -400, 0, const_a=0.35, const_b=0.75)
link(ring, rough, "Alpha")
MEL.connect_material_property(var, "", unreal.MaterialProperty.MP_BASE_COLOR)
MEL.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
MEL.connect_material_property(op, "", unreal.MaterialProperty.MP_OPACITY)
m.set_editor_property("material_domain", unreal.MaterialDomain.MD_DEFERRED_DECAL)
m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
EAL.save_asset(m.get_path_name(), only_if_is_dirty=False)

# ---- blueprint
P = "/Game/Timeshift/Hazards/BP_GeyserVent"
bp = EAL.load_asset(P)
if bp is None:
    f = unreal.BlueprintFactory()
    f.set_editor_property("parent_class", unreal.Actor)
    bp = tools.create_asset("BP_GeyserVent", "/Game/Timeshift/Hazards", unreal.Blueprint, f)
sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
LIB = unreal.SubobjectDataBlueprintFunctionLibrary
handles = sds.k2_gather_subobject_data_for_blueprint(bp)
have = {}
for h in handles:
    ob = LIB.get_object(sds.k2_find_subobject_data_from_handle(h))
    if ob:
        have.setdefault(ob.get_name().replace("_GEN_VARIABLE", ""), (h, ob))
root = handles[0]


def add(name, cls):
    if name in have:
        return have[name][1]
    h, fail = sds.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=root, new_class=cls, blueprint_context=bp))
    sds.rename_subobject(h, unreal.Text(name))
    ob = LIB.get_object(sds.k2_find_subobject_data_from_handle(h))
    have[name] = (h, ob)
    return ob


cap = add("Trigger", unreal.CapsuleComponent)
cap.set_editor_property("capsule_radius", 130.0)
cap.set_editor_property("capsule_half_height", 450.0)
cap.set_editor_property("relative_location", unreal.Vector(0, 0, 420))
cap.set_collision_profile_name("OverlapAllDynamic")
cap.set_editor_property("generate_overlap_events", True)
dec = add("Crust", unreal.DecalComponent)
dec.set_editor_property("decal_material", m)
dec.set_editor_property("decal_size", unreal.Vector(120, 260, 260))
dec.set_editor_property("relative_rotation", unreal.Rotator(0, -90, 0))
for name, asset, auto in (("Wisp", "NS_GeyserWisp", True), ("Warn", "NS_GeyserWarn", False), ("Steam", "NS_GeyserSteam", False)):
    nc = add(name, unreal.NiagaraComponent)
    nc.set_editor_property("asset", EAL.load_asset("/Game/Timeshift/Hazards/VFX/" + asset))
    nc.set_editor_property("auto_activate", auto)
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
EAL.save_asset(P, only_if_is_dirty=False)
unreal.log_warning("%s components %s | sounds %s" % (TAG, sorted(have.keys()),
                   [EAL.does_asset_exist("/Game/Timeshift/Hazards/Audio/" + n) for n in ("S_GeyserHiss", "S_GeyserBurst")]))
