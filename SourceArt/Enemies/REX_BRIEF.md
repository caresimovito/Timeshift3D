# T-Rex boss — build brief

Target: Unreal Engine 5.8 project at `C:\repos\Unreal Projects\Timeshift3D`.
Replaces `/Game/Timeshift/Enemies/RexPrime/SK_RexPrime`.

## What already exists and must keep working

`BP_Boss_RexPrime` holds all the AI (arena leash, bite cooldown, push-clear,
anim hold guard). It references these asset paths by name — match them exactly
and nothing in the blueprint needs changing:

    /Game/Timeshift/Enemies/RexPrime/SK_RexPrime
    /Game/Timeshift/Enemies/RexPrime/SK_RexPrime_Anim_SK_RexPrime_Idle
                                                        ..._Walk
                                                        ..._Run
                                                        ..._Attack
                                                        ..._Hit
                                                        ..._Death

## Mesh requirements

- ~13.2 m nose to tail. In Unreal that must read **1319 cm** on import — if it
  reads 13, the FBX unit scale was dropped.
- Facing **+X**, Z up, **pivot at the feet** (lowest vertex at z = 0).
- One connected shell. No loose fragments.
- Watertight: no boundary edges except the mouth. A previous version shipped
  with a 67-edge hole in the belly that was visible in game.
- Real **eyeball geometry**. A generated socket with nothing in it reads as a
  dark crease and looks wrong.
- 30-70k triangles is fine for a boss.

## The mouth — this is the hard requirement

The lower jaw must open and reveal a modelled interior. A hollow shell is
what killed two previous attempts; the gape had to be capped at 26 degrees
because anything wider showed an empty head.

- Lower jaw as a **separate shell**, split along the lip line.
- Both halves get a modelled, domed **palate and mouth floor** on their own
  material, so an open mouth shows anatomy and not a hole.
- Must open to at least **40 degrees** cleanly.
- If building the cavity in Blender: extrude the rim inward in ~3 concentric
  rings and cap. Do NOT fill the opening and poke it — that makes long thin
  triangles fanning from one centre which shade like crumpled paper. And
  `bmesh.ops.holes_fill(sides=6)` only closes holes of up to 6 edges; use
  `sides=0`.

## Rig — 26 bones, these exact names

    root, pelvis, spine_01, spine_02, spine_03,
    neck_01, neck_02, head, jaw,
    tail_01 .. tail_05,
    thigh_l/r, calf_l/r, foot_l/r, toe_l/r,
    upperarm_l/r, lowerarm_l/r

- `jaw` must drive the lower-jaw shell at **100% rigid weight**. Automatic
  heat weighting leaks the jaw bone onto the head and neck (4,738 verts last
  time) — strip anything that is not the jaw shell or the whole face swings
  open on a bite.
- Zero unweighted vertices.
- Roll the limb bones so local X is a clean fore/aft hinge. By default
  `thigh_l` local X moved the foot 1.17 m sideways, which left no usable
  stride axis.

## Animations — 30 fps, exported one FBX each

| Name   | Frames | Notes |
|--------|--------|-------|
| Idle   | ~90 | breathing, tail sway, mouth shut |
| Walk   | ~40 | stride ~3 m; 0.9 m reads as a shuffle on a 13 m animal |
| Run    | ~24 | longer stride, body pitched forward |
| Attack | ~30 | anticipation, lunge, jaw to ~45 deg, snap shut in 2-3 frames |
| Hit    | ~18 | sharp 2-frame recoil then settle |
| Death  | ~72 | stagger, legs buckle, topple, settle on the ground |

- Solve ground contact **numerically per frame** against the foot vertices so
  the planted foot sits ~2 cm above zero. Hand-authored pelvis bob sank the
  feet 0.25 m through the floor.
- The boss is moved by code (`SetActorLocation`), not root motion, so the
  animation is cosmetic — match the stride to his movement speed or the feet
  will skate.

## Export / import settings that matter

Blender FBX export: `axis_forward='-Z'`, `axis_up='Y'`, `global_scale=1.0`,
`apply_unit_scale=True`, `add_leaf_bones=False`, `use_armature_deform_only=True`.

Unreal import: `convert_scene=True`, `force_front_x_axis=False`,
`normal_import_method=FBXNIM_IMPORT_NORMALS`.

## Traps already hit — do not repeat

- **Embedded FBX textures do not import.** Interchange fails with "Invalid
  translator couldn't retrieve a payload". Import the PNGs separately.
- **FBX import creates `MaterialInstanceConstant`, not `Material`**, and
  `MaterialEditingLibrary` rejects instances. Build real Materials with
  `MaterialFactoryNew` and assign them to the slots.
- Texture settings: normal = `TC_NORMALMAP` + sRGB **off**; roughness and
  metallic sRGB **off**; base colour sRGB **on**.
- **`unreal.Rotator` is `Rotator(roll, pitch, yaw)`.** Writing
  `Rotator(0, 180, 0)` for a yaw sets PITCH 180 and flips the actor upside
  down. Unreal then normalises it to yaw 180 / roll -180, so it reads back
  looking plausible.
- **`get_actor_bounds` can return stale values** on an actor that has been
  moved repeatedly — it reported 1024 of height on a 512 model, a union of
  two positions. Verify with a freshly spawned actor instead.
- A deleted asset leaves component references **null**, not broken. A
  dependency check will report "0 broken references" and the mesh will still
  be invisible.

## Reference images (in this folder)

- **`trex.jpg`** — the four-panel reference sheet: side profile, oral cavity
  detail (palate / choanae / tongue / glottis labelled), front elevation,
  top-down plan. The oral cavity panel is the important one, because the
  mouth interior is the part generators get wrong.
- **`trex_side_clean.png`** — the side-profile panel cropped out, with the
  annotation arrows painted out. Use this one for any image-to-3D step: the
  arrows on the original get modelled as spikes, and a four-panel sheet
  confuses single-image generators.

Proportions taken off that sheet, as fractions of total length:
skull 0.14, neck 0.09, torso 0.22, tail 0.48, hip height 0.26, body depth
0.17. The tail cross-section at the hips is **tall and narrow**, not round.
